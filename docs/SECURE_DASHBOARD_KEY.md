# Secure Dashboard Key Generation

Encrypted dashboard mode uses `TRAFFIC_DASHBOARD_SECRET` to encrypt dashboard
data and, when needed, the retained Actions artifact. Anyone with this key can
decrypt the dashboard. GitHub will not show the secret value again after you
save it, so store it somewhere private.

Do not choose a memorable password. Generate a random dashboard key.

## Recommended: Password Manager

Use your password manager to generate a random password of at least 48
characters. Store it as `Reponomics dashboard key`, then paste it into the
repository secret named `TRAFFIC_DASHBOARD_SECRET`.

## Browser Console On A Blank Tab

Use this only on a new blank tab. Do not paste code into the browser console on
an untrusted website.

```js
(() => {
  const bytes = crypto.getRandomValues(new Uint8Array(32));
  return btoa(String.fromCharCode(...bytes))
    .replace(/\+/g, "-")
    .replace(/\//g, "_")
    .replace(/=+$/, "");
})()
```

Copy the generated value, store it somewhere private, and save it as
`TRAFFIC_DASHBOARD_SECRET`.

## Command Line

```sh
openssl rand -base64 32
```

```sh
node -e "console.log(require('crypto').randomBytes(32).toString('base64url'))"
```

## Rotation

1. Generate and save a new key.
2. Add it as `TRAFFIC_DASHBOARD_NEXT_SECRET`.
3. Run **Actions -> Rotate Reponomics dashboard key -> Run workflow**.
4. Replace `TRAFFIC_DASHBOARD_SECRET` with the new key.
5. Delete `TRAFFIC_DASHBOARD_NEXT_SECRET`.

If the old `TRAFFIC_DASHBOARD_SECRET` was deleted or overwritten before
rotation, the previous encrypted artifact cannot be recovered.

