def score_risk(result: dict) -> dict:
    score = 0
    factors = []

    http = result.get("http_headers") or {}
    status = http.get("status")
    headers = {str(k).lower(): str(v) for k, v in (http.get("headers") or {}).items()}

    if not status:
        score += 12
        factors.append("Main page HTTP fetch failed")

    # security headers baseline
    wanted = [
        "strict-transport-security",
        "content-security-policy",
        "x-frame-options",
        "x-content-type-options",
        "referrer-policy",
    ]
    missing = [h for h in wanted if h not in headers]
    if missing:
        s = min(20, len(missing) * 4)
        score += s
        factors.append(f"Missing security headers: {', '.join(missing)}")

    sec_txt = (result.get("security_txt") or {}).get("status")
    if sec_txt != 200:
        score += 8
        factors.append("security.txt missing or not reachable")

    emails = ((result.get("web") or {}).get("emails") or [])
    if emails:
        s = min(10, len(emails) * 2)
        score += s
        factors.append(f"Public emails exposed: {len(emails)}")

    subs = result.get("subdomains") or []
    if len(subs) > 80:
        score += 20
        factors.append(f"Large exposed subdomain surface: {len(subs)}")
    elif len(subs) > 20:
        score += 10
        factors.append(f"Medium exposed subdomain surface: {len(subs)}")

    errors = result.get("errors") or []
    if errors:
        s = min(15, len(errors) * 3)
        score += s
        factors.append(f"Collection errors observed: {len(errors)}")

    # plugin findings
    plugins = result.get("plugins") or {}
    plugin_items = 0
    for _, pdata in plugins.items():
        if isinstance(pdata, dict) and pdata.get("ok"):
            plugin_items += len(pdata.get("items") or [])
    if plugin_items > 30:
        score += 18
        factors.append(f"External engine findings volume high: {plugin_items}")
    elif plugin_items > 10:
        score += 10
        factors.append(f"External engine findings volume medium: {plugin_items}")

    score = max(0, min(100, score))

    if score >= 75:
        level = "critical"
    elif score >= 50:
        level = "high"
    elif score >= 25:
        level = "medium"
    else:
        level = "low"

    return {"score": score, "level": level, "factors": factors}
