# Reponomics Secrets And Configuration UX

Version: 0.1 intended design

The setup experience should help users choose a privacy model and generate a
strong dashboard secret without requiring terminal fluency.

## Dashboard Secret Requirements

`TRAFFIC_DASHBOARD_SECRET` should be:

- generated randomly
- at least 40 characters
- stored outside GitHub before saving as a repository secret
- treated as the decryption key for encrypted dashboard/artifact data

It should not be:

- a memorable password
- reused from another service
- recoverable from GitHub after saving

## Secret Generation Paths

### Terminal: OpenSSL

For terminal-literate users:

```sh
openssl rand -base64 32
```

Pros:

- fast
- local
- familiar to technical users

Cons:

- intimidating to non-terminal users
- output must still be saved in a password manager

### Browser DevTools Console

For users comfortable pasting a short command into a blank-tab console:

```js
(() => {
  const bytes = crypto.getRandomValues(new Uint8Array(32));
  return btoa(String.fromCharCode(...bytes))
    .replace(/\+/g, "-")
    .replace(/\//g, "_")
    .replace(/=+$/, "");
})()
```

Pros:

- no terminal required
- uses browser cryptographic randomness

Cons:

- users should never paste code into a console on an untrusted website
- requires careful instructions

### Hosted Static Key Generator

Reponomics should consider a static, client-side HTML page that generates a
dashboard key locally in the browser.

Requirements:

- no server round trip for generated key material
- no analytics on generated values
- no third-party scripts
- clear source link
- copy-to-clipboard button
- entropy explanation
- visible warning to store the key before saving it in GitHub

Possible fields:

- generated key
- estimated entropy bits
- character set and length
- "copy" button
- "regenerate" button
- "I stored this key" checklist

Entropy messaging:

- Estimates must be labeled as rough and illustrative.
- The page should avoid fake precision.
- It can compare weak human passwords to generated random keys to make the
  risk visible.
- It should explain that once encrypted output is published, attackers can
  download the ciphertext and guess offline.

Example copy:

> This generated key has about 256 bits of entropy. Under ordinary offline
> guessing assumptions, that is effectively infeasible to brute force. A short
> memorable password may be guessable in days or weeks.

## Privacy Modeler Page

Reponomics should consider a static "privacy modeler" page, either standalone
or part of docs, that helps users understand the consequences of each setup
choice.

Inputs:

- repository visibility: private/internal/public
- README dashboard: disabled/enabled
- Pages dashboard: disabled/encrypted/plain
- artifact mode: encrypted/plain
- local-only preference: yes/no

Outputs:

- who can see README metrics
- who can open the Pages dashboard
- who can access retained artifact data
- what data is committed to git
- what data is retained only as artifacts
- whether data can be deleted by deleting artifacts
- whether generated output may remain in git history

Important explanations:

- A private repository with README dashboard enabled discloses metrics to people
  with repository read access.
- A public repository can still use encrypted Pages output.
- Plain output means unencrypted output, regardless of repository visibility.
- Committed data is harder to erase than artifact data because git history and
  GitHub retention behavior may preserve prior states.
- Encrypted artifact mode is useful even when Pages output is disabled.

## Local-Only Path

Reponomics should consider a local workflow for users who do not want GitHub
Actions to publish outputs.

Possible commands:

- collect into a local clone
- restore/download artifacts
- render local HTML
- export standalone dashboard
- upload encrypted retained artifact only when desired

Use cases:

- users who want artifact-backed history but no committed dashboard output
- users who want to inspect data before publishing
- users with strict review requirements before committing metrics
- users using private repos but avoiding Pages entirely

Open questions:

- whether local collection should live in `reponomics-action`, a separate CLI,
  or both
- how local auth should be configured
- whether local collection should reuse Actions artifacts or store a local data
  directory only

