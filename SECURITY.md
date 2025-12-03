# Security Policy

## Supported Versions

We actively support the following versions with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

We take the security of the FVH Application Evaluator seriously. If you believe you've found a security vulnerability, please report it to us as described below.

**Please do not report security vulnerabilities through public GitHub issues.**

### Reporting Process

1. **Email**: Send details to security@forumvirium.fi
2. **Expected Response**: Within 48 hours
3. **Disclosure**: Coordinated disclosure after fix

### Information to Include

- Type of vulnerability
- Full paths of source file(s) affected
- Location of affected source code (tag/branch/commit)
- Step-by-step instructions to reproduce
- Proof-of-concept or exploit code (if possible)
- Impact of the vulnerability

### What to Expect

- Confirmation of receipt within 48 hours
- Regular updates on progress
- Credit in security advisory (if desired)
- Coordinated disclosure timeline

## Security Best Practices

### For Users

- Keep dependencies up to date
- Use secrets management (never commit secrets)
- Enable 2FA on accounts
- Review security advisories

### For Contributors

- Run `npm audit` (frontend) and `pip-audit` (backend) before submitting PRs
- Never commit secrets or credentials
- Use environment variables for configuration
- Follow secure coding guidelines

## Automated Security

This project uses:

- **Dependabot**: Automated dependency updates
- **CodeQL**: Static application security testing (SAST)
- **detect-secrets**: Pre-commit secret scanning
- **Dependency Review**: PR-level vulnerability checks

## Security Advisories

Security advisories are published through:

- GitHub Security Advisories
- Project release notes
