# OSINT Recon Report

Generated: 2026-03-03 14:53:59

Total targets: **1**

## Intelligence Timeline

- 2026-03-03T06:53:24.988759+00:00 | iana.org | risk=low (10)

## Target: iana.org

- Normalized: `https://iana.org`
- DNS A: 192.0.43.8
- HTTP Status: 200
- Final URL: https://www.iana.org/
- Title: Internet Assigned Numbers Authority
- Emails: N/A
- Passive subdomains: 21
- Plugin findings:
  - fofa: ERROR - missing FOFA_EMAIL / FOFA_KEY
  - shodan: ERROR - missing SHODAN_API_KEY
  - censys: ERROR - missing CENSYS_API_ID / CENSYS_API_SECRET
- Risk score: 10 (low)
  - Factors:
    - Medium exposed subdomain surface: 21
