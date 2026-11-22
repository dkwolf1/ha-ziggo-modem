# Security Policy

## Local modem connection

The integration uses HTTPS without certificate verification to support modems
with self-signed certificates. Traffic is encrypted, but the integration
cannot verify the identity of the modem. Use it only on a trusted local
network and do not expose the modem management interface to the internet.

## Reporting a vulnerability

Use [GitHub private vulnerability reporting](https://github.com/dkwolf1/ha-ziggo-modem/security/advisories/new)
for security issues in the Ziggo Modem integration. Please do not open a public
issue for an undisclosed vulnerability.

Include the installed integration and Home Assistant Core versions, the impact,
and enough context to investigate. If you include diagnostics or logs, review
them first and remove credentials, tokens, personal identifiers, and network
details that are not needed. Never include your modem password.

For vulnerabilities in Home Assistant itself, use the
[Home Assistant security policy](https://github.com/home-assistant/core/security/policy).
For ordinary integration bugs, use the
[public issue tracker](https://github.com/dkwolf1/ha-ziggo-modem/issues).
