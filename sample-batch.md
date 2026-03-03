# OSINT Recon Report

Generated: 2026-03-03 11:59:42

Total targets: **3**

## Target: example.com

- Normalized: `https://example.com`
- DNS A: 104.18.26.120, 104.18.27.120
- HTTP Status: N/A
- Final URL: N/A
- Title: N/A
- Emails: N/A
- Passive subdomains: 10
- Errors:
  - http_main: HTTPSConnectionPool(host='example.com', port=443): Max retries exceeded with url: / (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1032)')))
  - robots: HTTPSConnectionPool(host='example.com', port=443): Max retries exceeded with url: /robots.txt (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1032)')))
  - sitemap: HTTPSConnectionPool(host='example.com', port=443): Max retries exceeded with url: /sitemap.xml (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1032)')))
  - security_txt: HTTPSConnectionPool(host='example.com', port=443): Max retries exceeded with url: /.well-known/security.txt (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1032)')))

## Target: iana.org

- Normalized: `https://iana.org`
- DNS A: 192.0.43.8
- HTTP Status: 200
- Final URL: https://www.iana.org/
- Title: Internet Assigned Numbers Authority
- Emails: N/A
- Passive subdomains: 21

## Target: github.com

- Normalized: `https://github.com`
- DNS A: 20.205.243.166
- HTTP Status: 200
- Final URL: https://github.com/
- Title: GitHub · Change is constant. GitHub keeps you ahead. · GitHub
- Emails: you@domain.com
- Passive subdomains: 109
