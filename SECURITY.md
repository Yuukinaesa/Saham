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

## Security Practices

This application follows:

- **OWASP Top 10** mitigation
- **Input sanitization** on all user inputs
- **HTML escaping** for rendered content
- **Dependency version pinning** with upper bounds
- **No hardcoded secrets** (verified by automated tests)
- **Path traversal prevention** in file operations
- **XSS prevention** with link validation and content escaping
