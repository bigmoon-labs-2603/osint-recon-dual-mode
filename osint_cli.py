import argparse
import json
import sys

from batch_utils import run_batch
from osint_core import collect_osint, save_json
from plugins import parse_plugin_names, run_plugins
from report_export import export_docx, export_markdown, export_timeline_markdown
from risk_scoring import score_risk


def _read_targets_file(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]


def _enrich_item(item: dict, plugin_names: list[str], plugin_timeout: int, no_risk: bool):
    host = ((item.get("dns") or {}).get("host") or item.get("target_input") or "").strip()
    if plugin_names and host:
        item["plugins"] = run_plugins(host, plugin_names, timeout=plugin_timeout)
    else:
        item["plugins"] = {}

    if not no_risk:
        item["risk"] = score_risk(item)

    return item


def main():
    parser = argparse.ArgumentParser(description="OSINT Recon Dual Mode - CLI")
    parser.add_argument("--target", help="Single target domain/url/ip")
    parser.add_argument("--targets-file", help="Batch targets file (.txt), one target per line")
    parser.add_argument("--workers", type=int, default=5, help="Batch worker threads")

    parser.add_argument("--timeout", type=int, default=12, help="HTTP timeout seconds")
    parser.add_argument("--user-agent", default="OSINT-Recon-Dual-Mode/1.0", help="HTTP User-Agent")
    parser.add_argument("--no-verify-tls", action="store_true", help="Disable TLS verification (for lab/debug only)")
    parser.add_argument("--no-subdomains", action="store_true", help="Disable passive subdomain lookup")

    parser.add_argument("--plugins", default="", help="Comma separated plugins: fofa,shodan,censys")
    parser.add_argument("--plugin-timeout", type=int, default=15, help="Plugin HTTP timeout")
    parser.add_argument("--no-risk", action="store_true", help="Disable risk scoring")

    parser.add_argument("--out", default="", help="Output JSON file path")
    parser.add_argument("--export-md", default="", help="Export markdown report path")
    parser.add_argument("--export-docx", default="", help="Export docx report path")
    parser.add_argument("--export-timeline", default="", help="Export timeline markdown path")

    args = parser.parse_args()

    if not args.target and not args.targets_file:
        parser.error("Please provide --target or --targets-file")

    verify_tls = not args.no_verify_tls
    with_subdomains = not args.no_subdomains
    plugin_names = parse_plugin_names(args.plugins)

    try:
        if args.targets_file:
            targets = _read_targets_file(args.targets_file)
            result = run_batch(
                targets,
                workers=args.workers,
                timeout=args.timeout,
                user_agent=args.user_agent,
                verify_tls=verify_tls,
                with_subdomains=with_subdomains,
            )
            result = [_enrich_item(x, plugin_names, args.plugin_timeout, args.no_risk) for x in result]
        else:
            result = collect_osint(
                args.target,
                timeout=args.timeout,
                user_agent=args.user_agent,
                verify_tls=verify_tls,
                with_subdomains=with_subdomains,
            )
            result = _enrich_item(result, plugin_names, args.plugin_timeout, args.no_risk)

    except Exception as e:
        print(f"[!] failed: {e}", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(result, ensure_ascii=False, indent=2))

    if args.out:
        save_json(result, args.out)
        print(f"[+] saved json => {args.out}")

    if args.export_md:
        export_markdown(result, args.export_md)
        print(f"[+] saved markdown => {args.export_md}")

    if args.export_docx:
        export_docx(result, args.export_docx)
        print(f"[+] saved docx => {args.export_docx}")

    if args.export_timeline:
        export_timeline_markdown(result, args.export_timeline)
        print(f"[+] saved timeline => {args.export_timeline}")


if __name__ == "__main__":
    main()
