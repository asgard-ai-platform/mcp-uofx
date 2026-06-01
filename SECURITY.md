# Security Policy

## Supported Versions

This repository is currently pre-1.0. Security fixes are applied to the latest `main` branch.

## Reporting a Vulnerability

Do not open a public issue for secrets, credentials, tokens, authorization bypasses, or data exposure reports.

Report privately to the repository maintainers through your normal security contact channel. Include:

- A clear description of the issue.
- A minimal reproduction if possible.
- Affected files, commands, or configuration.
- Whether any credential, token, hostname, user data, or customer data was exposed.

## Credential Handling

- Never commit `.env`, API keys, OAuth client secrets, access tokens, refresh tokens, generated reports, or local credential files.
- OAuth credentials are stored locally under `~/.uofx/credentials.json` and should not be copied into this repository.
- Use `.env.example` for placeholders only.
- Treat manual integration outputs as sensitive unless reviewed and sanitized.

## Deployment Notes

- `UOFX_VERIFY_SSL=false` is only intended for test environments with incomplete certificates.
- Use strict SSL verification in production.
- The SSE demo token mechanism is for local testing. Replace it with real token verification before deploying an exposed service.
