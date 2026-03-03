import argparse
import json
import sys

from osint_core import collect_osint, save_json


def main():
    parser = argparse.ArgumentParser(description="OSINT Recon Dual Mode - CLI")
    parser.add_argument("--target", required=True, help="Target domain/url/ip")
    parser.add_argument("--timeout", type=int, default=12, help="HTTP timeout seconds")
    parser.add_argument("--user-agent", default="OSINT-Recon-Dual-Mode/1.0", help="HTTP User-Agent")
    parser.add_argument("--no-verify-tls", action="store_true", help="Disable TLS verification (for lab/debug only)")
    parser.add_argument("--no-subdomains", action="store_true", help="Disable passive subdomain lookup")
    parser.add_argument("--out", default="", help="Output JSON file path")
    args = parser.parse_args()

    try:
        result = collect_osint(
            args.target,
            timeout=args.timeout,
            user_agent=args.user_agent,
            verify_tls=not args.no_verify_tls,
            with_subdomains=not args.no_subdomains,
        )
    except Exception as e:
        print(f"[!] failed: {e}", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(result, ensure_ascii=False, indent=2))

    if args.out:
        save_json(result, args.out)
        print(f"\n[+] saved => {args.out}")


if __name__ == "__main__":
    main()
