# Security Policy

## Supported Versions

We release patches for security vulnerabilities. Which versions are eligible for receiving such patches depends on the CVSS v3.0 Rating:

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

Please report (suspected) security vulnerabilities to **support@robocompute.xyz**. You will receive a response within 48 hours. If the issue is confirmed, we will release a patch as soon as possible depending on complexity but historically within a few days.

## Security Best Practices

### API Keys

- Never commit API keys to version control
- Rotate API keys regularly
- Use environment variables or secure secret management
- Use different API keys for development and production

### Wallet Security

- Never share your Solana wallet private keys
- Use hardware wallets for production environments
- Keep wallet software updated
- Use separate wallets for different purposes

### Network Security

- Always use HTTPS/WSS for API connections
- Verify SSL certificates
- Use secure RPC endpoints for Solana

### Code Security

- Keep dependencies updated
- Review code changes before deployment
- Use dependency scanning tools
- Follow secure coding practices

## Disclosure Policy

When the security team receives a security bug report, they will assign it to a primary handler. This person will coordinate the fix and release process, involving the following steps:

1. Confirm the problem and determine the affected versions
2. Audit code to find any potential similar problems
3. Prepare fixes for all releases still under maintenance
4. Release a security advisory

## Security Updates

Security updates will be released as patch versions (e.g., 1.0.1, 1.0.2) and will be clearly marked in the changelog.

