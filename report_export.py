import json
import zipfile
from datetime import datetime
from pathlib import Path
from xml.sax.saxutils import escape


def _md_for_single(r: dict) -> str:
    lines = []
    lines.append(f"## Target: {r.get('target_input', '')}")
    lines.append("")
    lines.append(f"- Normalized: `{r.get('normalized', '')}`")

    dns = (r.get("dns") or {}).get("a_records", [])
    lines.append(f"- DNS A: {', '.join(dns) if dns else 'N/A'}")

    http = r.get("http_headers") or {}
    lines.append(f"- HTTP Status: {http.get('status', 'N/A')}")
    lines.append(f"- Final URL: {http.get('final_url', 'N/A')}")

    web = r.get("web") or {}
    lines.append(f"- Title: {web.get('title', '') or 'N/A'}")
    emails = web.get("emails") or []
    lines.append(f"- Emails: {', '.join(emails) if emails else 'N/A'}")

    subdomains = r.get("subdomains") or []
    lines.append(f"- Passive subdomains: {len(subdomains)}")

    risk = r.get("risk") or {}
    if risk:
        lines.append(f"- Risk: **{risk.get('level', 'n/a')}** ({risk.get('score', 'n/a')}/100)")

    plugins = r.get("plugins") or {}
    if plugins:
        lines.append("- Plugin findings:")
        for name, pdata in plugins.items():
            if isinstance(pdata, dict) and pdata.get("ok"):
                lines.append(f"  - {name}: {len(pdata.get('items') or [])}")
            else:
                lines.append(f"  - {name}: error")

    errs = r.get("errors") or []
    if errs:
        lines.append("- Errors:")
        for e in errs:
            lines.append(f"  - {e}")

    lines.append("")
    return "\n".join(lines)


def export_markdown(result, out_path: str):
    p = Path(out_path)
    p.parent.mkdir(parents=True, exist_ok=True)

    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = ["# OSINT Recon Report", "", f"Generated: {ts}", ""]

    if isinstance(result, list):
        lines.append(f"Total targets: **{len(result)}**")
        lines.append("")
        for r in result:
            lines.append(_md_for_single(r))
    else:
        lines.append(_md_for_single(result))

    p.write_text("\n".join(lines), encoding="utf-8")


def export_timeline_markdown(result, out_path: str):
    p = Path(out_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    items = result if isinstance(result, list) else [result]

    lines = ["# OSINT Timeline", "", f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ""]
    for r in items:
        ts = r.get("timestamp", "")
        tgt = r.get("target_input", "")
        risk = r.get("risk") or {}
        lines.append(f"- [{ts}] {tgt} | risk={risk.get('level','n/a')}({risk.get('score','n/a')})")
        plugins = r.get("plugins") or {}
        for name, pdata in plugins.items():
            if isinstance(pdata, dict) and pdata.get("ok"):
                lines.append(f"  - plugin:{name} hits={len(pdata.get('items') or [])}")
        errs = r.get("errors") or []
        if errs:
            lines.append(f"  - errors={len(errs)}")
    lines.append("")

    p.write_text("\n".join(lines), encoding="utf-8")


def export_docx(result, out_path: str):
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    if isinstance(result, list):
        payload = {
            "generated": datetime.now().isoformat(),
            "total": len(result),
            "items": result,
        }
    else:
        payload = {
            "generated": datetime.now().isoformat(),
            "total": 1,
            "items": [result],
        }

    pretty = json.dumps(payload, ensure_ascii=False, indent=2)

    doc = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p><w:r><w:t>OSINT Recon Report</w:t></w:r></w:p>
    <w:p><w:r><w:t xml:space="preserve">{escape(pretty)}</w:t></w:r></w:p>
    <w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440"/></w:sectPr>
  </w:body>
</w:document>'''

    content_types = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>'''

    rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>'''

    doc_rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>'''

    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types)
        z.writestr("_rels/.rels", rels)
        z.writestr("word/document.xml", doc)
        z.writestr("word/_rels/document.xml.rels", doc_rels)
