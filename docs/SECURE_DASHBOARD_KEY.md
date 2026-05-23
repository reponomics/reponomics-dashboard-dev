# Secure Dashboard Key Generation

`privacy-mode=strong` and `privacy-mode=casual` use
`TRAFFIC_DASHBOARD_SECRET` to encrypt retained artifacts and hosted dashboard
data. Anyone with this key can decrypt the dashboard and CSV export. GitHub
will not show the secret value again after you save it, so store it somewhere
private.

Do not choose a memorable password for `strong`. Generate a random dashboard
key.

## Recommended: Command Line

Use a shell-safe 256-bit hex key:

```sh
openssl rand -hex 32
```

Save the generated value in a password manager, then add it as the repository
secret named `TRAFFIC_DASHBOARD_SECRET`.

## Password Manager

Use your password manager to generate a random password of at least 64
characters. Store it as `Reponomics dashboard key`, then paste it into the
repository secret named `TRAFFIC_DASHBOARD_SECRET`.

## Browser Console On A Blank Tab

Use this only on a new blank tab. Do not paste code into the browser console on
an untrusted website.

```js
Array.from(crypto.getRandomValues(new Uint8Array(32)), (byte) =>
  byte.toString(16).padStart(2, "0")
).join("")
```

Copy the generated value, store it somewhere private, and save it as
`TRAFFIC_DASHBOARD_SECRET`.

## Strong Versus Casual

`strong` requires a generated, high-entropy secret. Setup rejects short secrets
for this mode.

`casual` accepts any non-empty secret and still encrypts artifacts and hosted
dashboard output, but weak or shared secrets can be brute-forced offline from
the encrypted payload. Use it only when the goal is preventing accidental
viewing, crawling, or casual discovery.

`plain` does not use a dashboard secret. It stores retained CSV artifacts
without encryption and is only supported in private repositories.

## Rotation

1. Generate and save a new key.
2. Add it as `TRAFFIC_DASHBOARD_NEXT_SECRET`.
3. Run **Actions -> Rotate Reponomics dashboard key -> Run workflow**.
4. Confirm the dashboard opens with the new key.
5. Replace `TRAFFIC_DASHBOARD_SECRET` with the new key.
6. Delete `TRAFFIC_DASHBOARD_NEXT_SECRET`.

If the old `TRAFFIC_DASHBOARD_SECRET` was deleted or overwritten before
rotation, the previous encrypted artifact cannot be recovered.
