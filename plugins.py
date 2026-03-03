import base64
import os

try:
    import requests
except Exception:
    requests = None


def parse_plugin_names(raw: str):
    if not raw:
        return []
    return [x.strip().lower() for x in raw.split(",") if x.strip()]


def _err(name: str, msg: str):
    return {"plugin": name, "ok": False, "error": msg, "items": []}


def _ok(name: str, items, meta=None):
    return {"plugin": name, "ok": True, "items": items, "meta": meta or {}}


def run_plugins(host: str, plugin_names: list[str], timeout: int = 15):
    out = {}
    for p in plugin_names:
        p = (p or "").lower()
        if p == "fofa":
            out[p] = query_fofa(host, timeout)
        elif p == "shodan":
            out[p] = query_shodan(host, timeout)
        elif p == "censys":
            out[p] = query_censys(host, timeout)
        else:
            out[p] = _err(p, "unknown plugin")
    return out


def query_fofa(host: str, timeout: int = 15):
    if not requests:
        return _err("fofa", "requests not available")

    email = os.getenv("FOFA_EMAIL", "").strip()
    key = os.getenv("FOFA_KEY", "").strip()
    if not email or not key:
        return _err("fofa", "missing FOFA_EMAIL / FOFA_KEY")

    q = f'domain="{host}" || host="{host}"'
    qbase64 = base64.b64encode(q.encode("utf-8")).decode("utf-8")
    url = "https://fofa.info/api/v1/search/all"
    params = {
        "email": email,
        "key": key,
        "qbase64": qbase64,
        "size": 10,
        "fields": "host,ip,port,protocol,title,domain",
    }

    try:
        r = requests.get(url, params=params, timeout=timeout)
        data = r.json()
        if not data.get("error") is False:
            return _err("fofa", str(data.get("errmsg", "fofa api error")))

        items = []
        for row in data.get("results", []) or []:
            items.append(
                {
                    "host": row[0] if len(row) > 0 else "",
                    "ip": row[1] if len(row) > 1 else "",
                    "port": row[2] if len(row) > 2 else "",
                    "protocol": row[3] if len(row) > 3 else "",
                    "title": row[4] if len(row) > 4 else "",
                    "domain": row[5] if len(row) > 5 else "",
                }
            )
        return _ok("fofa", items, {"query": q})
    except Exception as e:
        return _err("fofa", str(e))


def query_shodan(host: str, timeout: int = 15):
    if not requests:
        return _err("shodan", "requests not available")

    key = os.getenv("SHODAN_API_KEY", "").strip()
    if not key:
        return _err("shodan", "missing SHODAN_API_KEY")

    url = "https://api.shodan.io/shodan/host/search"
    params = {"key": key, "query": f"hostname:{host}"}

    try:
        r = requests.get(url, params=params, timeout=timeout)
        data = r.json()
        if "error" in data:
            return _err("shodan", str(data.get("error")))

        items = []
        for m in data.get("matches", [])[:10]:
            items.append(
                {
                    "ip": m.get("ip_str", ""),
                    "port": m.get("port", ""),
                    "org": m.get("org", ""),
                    "hostnames": m.get("hostnames", []),
                }
            )
        return _ok("shodan", items, {"total": data.get("total", 0)})
    except Exception as e:
        return _err("shodan", str(e))


def query_censys(host: str, timeout: int = 15):
    if not requests:
        return _err("censys", "requests not available")

    api_id = os.getenv("CENSYS_API_ID", "").strip()
    api_secret = os.getenv("CENSYS_API_SECRET", "").strip()
    if not api_id or not api_secret:
        return _err("censys", "missing CENSYS_API_ID / CENSYS_API_SECRET")

    url = "https://search.censys.io/api/v2/hosts/search"
    payload = {"q": host, "per_page": 10}

    try:
        r = requests.post(url, json=payload, auth=(api_id, api_secret), timeout=timeout)
        data = r.json()
        if r.status_code >= 400:
            return _err("censys", str(data))

        hits = (((data or {}).get("result") or {}).get("hits") or [])
        items = []
        for h in hits:
            items.append(
                {
                    "ip": h.get("ip", ""),
                    "services": [
                        {"port": s.get("port", ""), "service_name": s.get("service_name", "")}
                        for s in (h.get("services") or [])[:10]
                    ],
                }
            )
        return _ok("censys", items, {"query": host})
    except Exception as e:
        return _err("censys", str(e))
