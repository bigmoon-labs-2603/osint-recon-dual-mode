import json
import re
import socket
import ssl
from datetime import datetime, timezone
from urllib.parse import urlparse
from urllib.request import Request, urlopen

try:
    import requests  # optional
except Exception:
    requests = None

from plugins import run_plugins
from risk_scoring import score_risk

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.I | re.S)


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


def _http_get(url: str, timeout: int = 12, user_agent: str = "OSINT-Recon-Dual-Mode/1.0", verify_tls: bool = True):
    headers = {"User-Agent": user_agent}
    if requests:
        r = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True, verify=verify_tls)
        return {
            "url": r.url,
            "status": r.status_code,
            "headers": dict(r.headers),
            "text": r.text,
        }

    req = Request(url, headers=headers)
    context = None
    if not verify_tls:
        context = ssl._create_unverified_context()

    with urlopen(req, timeout=timeout, context=context) as resp:
        data = resp.read().decode("utf-8", errors="ignore")
        return {
            "url": resp.geturl(),
            "status": getattr(resp, "status", 200),
            "headers": dict(resp.headers.items()),
            "text": data,
        }


def _extract_title(html: str) -> str:
    m = TITLE_RE.search(html or "")
    return m.group(1).strip() if m else ""


def _fetch_crtsh_subdomains(host: str, timeout: int = 12) -> list[str]:
    if not requests:
        return []
    url = f"https://crt.sh/?q=%25.{host}&output=json"
    r = requests.get(url, timeout=timeout)
    if r.status_code != 200:
        return []
    names = set()
    try:
        arr = r.json()
    except Exception:
        return []
    for item in arr:
        v = (item.get("name_value") or "").strip()
        if not v:
            continue
        for n in v.splitlines():
            n = n.strip().lower()
            if n.startswith("*."):
                n = n[2:]
            if n:
                names.add(n)
    return sorted(names)


def collect_osint(
    target: str,
    timeout: int = 12,
    user_agent: str = "OSINT-Recon-Dual-Mode/1.0",
    verify_tls: bool = True,
    with_subdomains: bool = True,
    plugin_names: list[str] | None = None,
    enable_risk: bool = True,
) -> dict:
    normalized = _normalize_target(target)
    host = _hostname_from_target(normalized)

    result = {
        "target_input": target,
        "normalized": normalized,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "dns": {},
        "http_headers": {},
        "web": {"title": "", "emails": []},
        "robots": {},
        "sitemap": {},
        "security_txt": {},
        "subdomains": [],
        "plugins": {},
        "risk": {},
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
        main = _http_get(normalized, timeout=timeout, user_agent=user_agent, verify_tls=verify_tls)
        result["http_headers"] = {
            "final_url": main.get("url"),
            "status": main.get("status"),
            "headers": main.get("headers", {}),
        }
        page_text = main.get("text", "") or ""
        result["web"]["title"] = _extract_title(page_text)
    except Exception as e:
        result["errors"].append(f"http_main: {e}")

    # robots / sitemap / security.txt
    checks = (
        ("robots", "/robots.txt"),
        ("sitemap", "/sitemap.xml"),
        ("security_txt", "/.well-known/security.txt"),
    )
    for key, suffix in checks:
        try:
            base = normalized.rstrip("/")
            info = _http_get(base + suffix, timeout=timeout, user_agent=user_agent, verify_tls=verify_tls)
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
    result["web"]["emails"] = emails

    # passive subdomains
    if with_subdomains:
        try:
            result["subdomains"] = _fetch_crtsh_subdomains(host, timeout=timeout)
        except Exception as e:
            result["errors"].append(f"crtsh: {e}")

    # plugin engines
    if plugin_names:
        try:
            result["plugins"] = run_plugins(host, plugin_names, timeout=timeout)
        except Exception as e:
            result["errors"].append(f"plugins: {e}")

    # risk scoring
    if enable_risk:
        try:
            result["risk"] = score_risk(result)
        except Exception as e:
            result["errors"].append(f"risk: {e}")

    return result


def save_json(data: dict, out_file: str):
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
