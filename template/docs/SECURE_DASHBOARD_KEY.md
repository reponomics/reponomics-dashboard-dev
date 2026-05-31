# Secure Dashboard Key Generation

For `privacy-mode=strong`, generate a high-entropy secret for `DASHBOARD_SECRET_DO_NOT_REPLACE`.

## Recommended

- Use at least 40 random characters (or equivalent entropy).
- Store the value in a password manager or other secure secret store.
- Keep a recovery copy before any key rotation.

## Rotation

Use the provided rotate-key workflow and follow repository docs. Do not overwrite `DASHBOARD_SECRET_DO_NOT_REPLACE` directly as a substitute for rotation.
