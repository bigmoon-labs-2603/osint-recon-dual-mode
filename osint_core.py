import json
import re
import socket
from datetime import datetime, timezone
from urllib.parse import urlparse
from urllib.request import Request, urlopen

try:
    import requests  # optional
except Exception:
    requests = None

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")


def _normalize_target(target: str) -> str:
    t = target.strip()
    if not t:
        raise ValueError("target is empty")
    if not t.startswith(("http://", "https://")):
        t = "https://" + t
    return t


def _hostname_from_target(target: str) -> str:
    p = urlparse(target)
    return p.hostname or target


def _http_get(url: str, timeout: int = 12, user_agent: str = "OSINT-Recon-Dual-Mode/1.0"):
    headers = {"User-Agent": user_agent}
    if requests:
        r = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        return {
            "url": r.url,
            "status": r.status_code,
            "headers": dict(r.headers),
            "text": r.text,
        }
    req = Request(url, headers=headers)
    with urlopen(req, timeout=timeout) as resp:
        data = resp.read().decode("utf-8", errors="ignore")
        return {
            "url": resp.geturl(),
            "status": getattr(resp, "status", 200),
            "headers": dict(resp.headers.items()),
            "text": data,
        }


def collect_osint(target: str, timeout: int = 12, user_agent: str = "OSINT-Recon-Dual-Mode/1.0") -> dict:
    normalized = _normalize_target(target)
    host = _hostname_from_target(normalized)

    result = {
        "target_input": target,
        "normalized": normalized,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "dns": {},
        "http_headers": {},
        "robots": {},
        "sitemap": {},
        "emails": [],
        "errors": [],
    }

    # DNS
    try:
        _, _, ips = socket.gethostbyname_ex(host)
        result["dns"] = {"host": host, "a_records": sorted(set(ips))}
    except Exception as e:
        result["dns"] = {"host": host, "a_records": []}
        result["errors"].append(f"dns: {e}")

    # Main page
    page_text = ""
    try:
        main = _http_get(normalized, timeout=timeout, user_agent=user_agent)
        result["http_headers"] = {
            "final_url": main.get("url"),
            "status": main.get("status"),
            "headers": main.get("headers", {}),
        }
        page_text = main.get("text", "") or ""
    except Exception as e:
        result["errors"].append(f"http_main: {e}")

    # robots / sitemap
    for key, suffix in (("robots", "/robots.txt"), ("sitemap", "/sitemap.xml")):
        try:
            base = normalized.rstrip("/")
            info = _http_get(base + suffix, timeout=timeout, user_agent=user_agent)
            result[key] = {
                "url": info.get("url"),
                "status": info.get("status"),
                "length": len(info.get("text", "") or ""),
            }
        except Exception as e:
            result[key] = {"url": normalized.rstrip("/") + suffix, "status": None, "length": 0}
            result["errors"].append(f"{key}: {e}")

    # emails
    emails = sorted(set(x.lower() for x in EMAIL_RE.findall(page_text)))
    result["emails"] = emails

    return result


def save_json(data: dict, out_file: str):
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
