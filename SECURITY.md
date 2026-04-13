# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| Latest  | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability, please report it responsibly:

1. **Do NOT** create a public GitHub issue
2. Email the maintainer directly
3. Include steps to reproduce
4. Allow 48 hours for an initial response

## Security Architecture

### Defense Layers

| Layer | Protection | Implementation |
|-------|-----------|----------------|
| **Input** | Injection Prevention | `sanitize_stock_symbol()`, `sanitize_url()`, `validate_numeric_input()` |
| **Processing** | Rate Limiting | Token-bucket limiter on Yahoo Finance (30/min) and RSS feeds (20/min) |
| **Output** | XSS Prevention | HTML escaping via `html.escape()`, URL scheme validation |
| **Network** | Security Headers | CSP, X-Frame-Options DENY, Permissions-Policy, HSTS |
| **Data** | Path Traversal Prevention | Config file validation, whitelisted keys only |
| **Config** | Server Hardening | CORS enabled, XSRF protection enabled, upload limits |

### OWASP Top 10 Coverage

| # | Vulnerability | Status | Implementation |
|---|--------------|--------|----------------|
| A01 | Broken Access Control | ✅ Mitigated | Path traversal checks in `state_manager.py` |
| A02 | Cryptographic Failures | ✅ N/A | No secrets stored; env vars for configuration |
| A03 | Injection | ✅ Mitigated | Input sanitization on all user inputs; URL encoding in RSS queries |
| A04 | Insecure Design | ✅ Mitigated | Input bounds on calculators; rate limiting |
| A05 | Security Misconfiguration | ✅ Mitigated | Server config hardened; CORS/XSRF enabled |
| A06 | Vulnerable Components | ✅ Mitigated | Pinned dependencies with upper version bounds |
| A07 | Auth Failures | ✅ N/A | No authentication required (read-only financial app) |
| A08 | Data Integrity Failures | ✅ Mitigated | Financial logic boundary tests; division-by-zero guards |
| A09 | Logging Failures | ✅ Mitigated | Structured JSON logging via `logger.py` |
| A10 | SSRF | ✅ Mitigated | URL validation; only whitelisted domains in RSS feeds |

## Security Practices

This application follows:

- **OWASP Top 10** mitigation (all 10 categories addressed)
- **Input sanitization** on all user inputs (`sanitize_stock_symbol`, `validate_numeric_input`)
- **HTML escaping** for rendered content (`html.escape()` in news cards)
- **URL validation** preventing `javascript:` and `data:` protocol XSS
- **Dependency version pinning** with upper bounds (supply chain protection)
- **No hardcoded secrets** (verified by automated tests in CI/CD)
- **Path traversal prevention** in file operations (whitelisted keys)
- **Rate limiting** on external API calls (Yahoo Finance, RSS feeds)
- **Structured audit logging** with JSON output (NIST SP 800-92)
- **Security headers** (X-Frame-Options, Permissions-Policy, X-Content-Type-Options)
- **CORS and XSRF protection** enabled in Streamlit server config
- **DoS prevention** via input value caps and iteration limits

## Incident Response Plan

### Severity Levels

| Level | Description | Response Time | Example |
|-------|------------|---------------|---------|
| **P0 Critical** | Data breach, secret exposure | < 1 hour | API key leak in commit |
| **P1 High** | Active exploitation possible | < 4 hours | XSS in user-facing content |
| **P2 Medium** | Vulnerability found, not exploited | < 24 hours | Missing input validation |
| **P3 Low** | Minor security improvement | < 1 week | Better error messages |

### Response Procedure

1. **Identify**: Check `logs/audit.log` for security events
2. **Contain**: Disable affected feature or rate limit aggressively
3. **Eradicate**: Apply fix and deploy
4. **Recover**: Verify fix in production
5. **Learn**: Update security tests to prevent recurrence

### Automated Security Checks

- **CI/CD Pipeline** (`.github/workflows/tests.yml`): Runs on every push/PR
  - Unit tests (53+ tests covering security boundaries)
  - Hardcoded secret scanning
  - Dependency version bound validation
  - Python syntax validation
- **Audit Tests** (`tests/test_audit.py`): Code quality and hygiene
- **Security Tests** (`tests/test_security.py`): Input sanitization, XSS prevention, URL validation

## Dependency Management

All dependencies are pinned with both lower and upper version bounds to prevent supply chain attacks:

```
streamlit>=1.28.0,<2.0.0
yfinance>=0.2.0,<1.0.0
pandas>=1.0.0,<3.0.0
```

Review and update bounds quarterly or when CVEs are published.
