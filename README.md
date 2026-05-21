# Reponomics Dashboard

Welcome to your personal GitHub BI dashboard.

Every repo you own is full of data, delivered to you hourly by GitHub itself - view count, unique visitors, clones, top referring sites, and most popular pages. GitHub provides this data to every repo, for free - tucked away in a tab under Insights > Traffic. If you're trying to launch an app, or grow your user base, this data can unlock key metrics that will help you reach your goals, and understand your growth. The problem is it's not so easy to take advantage of that data.

## 1) The 14-Day Window

If you want insights into your repo's traffic over the past 14 days, it's only a few clicks away. But what if you want that _same_ data one month from now. Were you storing it? If not, unfortunately it's gone for good. There's no API to get it from. There's just a rolling 14-day window of insights, and every day the tail of that window disappears. The Reponomics Dashboard allows you start collecting that data _today_. Maybe you're not even sure if you'll want it in one month - but unless you start collecting it now, if you decide you _do_ want to take a look at it, you might have missed your chance.

## 2) A Different Page for Every Repo

Now, suppose you have more than one repo where you have an amazing app and you want to analyze its growth. Well, GitHub is generous enough to give you that 14-day window of data, for all of these repos - but they don't give you a _unified_ window where you can look at all of that data at once. And if you're building more than one app, you probably want to see how they're performing relative to one another. You don't just want to collect the data, you want to aggregate it, and analyze it, and compare it. This template repo allows you to do all of those things, in a clear HTML dashboard. That's pretty cool - but it's not even the cool part.

## Private Data, Public Hosting

There's a reason why repo Traffic data is only visible to users with push access to the repository - it's private information, and you might want to keep it that way. So, if you want a website where you can view that data and interact with it, you have to find a place to host it - which usually costs you time and money. Which is a shame because  every repo has a free static site hosting option in the form of GitHub Pages. The only problem is - whether your repo is public or private, your GitHub Pages site is public.

The Reponomics Dashboard template repo solves this problem for you - public website, private data. When you create a repo based off of this template, you start by setting up a private key. There's a number of ways you can create a key, or a password - the only important thing is to make sure that it's _really, really long_. Once you create your key, you store it somewhere accessible, like your password manager, or your Keychain, and then you save it to the repository as a repo secret. Now you're ready to get going - that's all the setup you need.

Once you've set up your repo secret, you're ready to start collecting Traffic data from any repository where you have access to it, and it will _never be stored anywhere in plain text_. Twice a day, a workflow will go around to whatever repositories you've configured it to collect from, it will query for that data, write it all down to a CSV file, _encrypt the CSV file_ using your very, very long password, and then upload it as a workflow artifact. The plain text data never lands in your repo's source code. Then, assuming you want that nice HTML dashboard, the publish workflow renders the dashboard shell, encrypts the dashboard data into that shell, and deploys it to GitHub Pages. Your private dashboard is open to the public - that's true. But it's only served in an encrypted form. Then when you visit the dashboard, if you know the repository secret, you enter that into the password field, and the dashboard is decrypted using strictly client-side decryption.

### It Couldn't Be Any Easier

What's the upshot? Persistent storage of ephemeral data; aggregated across multiple repos; collected and immediately encrypted before it's uploaded as a workflow artifact; and then served via GitHub Pages in encrypted form. All of it for free - no third parties - no external APIs or services - no plaintext data stored anywhere - and all of it is under your control. You decide what to do with the data, whether you want to host it on GitHub Pages, download the dashboard and view it offline, or just keep it stored as an artifact for some future use yet to be determined. As long as you have the repo secret, it's all being aggregated in a CSV file that you can decrypt whenever you decide you want to use it. And if you happen to forget that extremely long password? That's OK too. So long as you have control of the repository's workflows, you can rotate the key any time you want.

#### ***This even works for public repos and free accounts.***

That's what the Reponomics Dashboard template repo offers you - a way to actually _do something_ with all that valuable data that GitHub is sending you, make it last longer than the 14-day expiration date, aggregate it across your repos, and provide you with a turnkey solution for private, encrypted hosting of your analytics dashboard using GitHub's freely provided public infrastructure. Ready to get started?

## Quick Setup

Choose your privacy model:

<details>
<summary align="absmiddle">Private Repo, Private GitHub Pages Dashboard</summary>

1. Create a repository from this template.

2. In order to collect the data at all, you'll need a _personal access token_ with the necessary permissions for the repos you're tracking. Once you generate that, store it as a repository secret named `TRAFFIC_TOKEN`.

3. In order to _encrypt_ the data, you'll need an encryption key - see [here](TBD) for information on how to generate that key. ***If you really want moderately strong privacy, it has to be a very long key.*** It's really important to understand that before you start down the wrong path. For information about why, read more about it [here](TBD). This repo does _not_ provide enterprise-level privacy suitable for critically sensitive information. And what it does provide is _entirely_ dependent on having a very strong password. But either way, you decide whatever privacy model suits your needs. If you're not really sure, and this is all sounds a bit confusing, consider following these instructions for maximum privacy.

4. Store the encryption secret in the repository as `TRAFFIC_DASHBOARD_SECRET`. This will be used during the collection workflow to decrypt the stored data, write the newly collected data to it, and then immediately encrypt it before it's uploaded as an artifact. Additionally, the publish workflow uses it to render and deploy an encrypted dashboard shell to GitHub Pages.

5. head over to the Actions tab, and run **Actions -> Set up Reponomics dashboard -> Run workflow**.
</details>
II. Private Repo, No GitHub Pages
III. Public Repo, Private Data
IV. Public Repo, Public Data

1. Create a repository from this template.
2. In order to collect the data at all, you'll need a _personal access token_ with the necessary permissions for the repos you're tracking. Once you generate that, store it as a repository secret named `TRAFFIC_TOKEN`.
3. In order to _encrypt_ the data, you'll need an encryption key - see [here](TBD) for information on how to generate that key. ***If you really want moderately strong privacy, it has to be a very long key.*** It's really important to understand that before you start down the wrong path. For information about why, read more about it [here](TBD). This repo does _not_ provide enterprise-level privacy suitable for critically sensitive information. And what it does provide is _entirely_ dependent on having a very strong password. But either way, you decide whatever privacy model suits your needs. If you're not really sure, and this is all sounds a bit new to you, consider following the instructions for maximum privacy.
4. If you have a _private_ repo, and you don't want a GitHub Pages site, then you might be fine without having an encryption key at all. In that case, the privacy boundary is just: whoever has access to the repo can download the artifacts that store your data. Everything will be stored in plaintext, but only those with repo access can access the data. It's only if you want to serve that data on the open internet that you would need to encrypt it.
5. If you are using a _public_ repo, then everything is available for anyone to read. So if you care about the privacy of that data at all (which, again, is up to you), then the encryption key is necessary.
6. So, with that in mind, if you want to encrypt your data, you generate your key, and store it again as a repository secret called `TRAFFIC_DASHBOARD_SECRET`. This will be used during the collection workflow to decrypt the stored data, write the newly collected data to it, and then immediately encrypt it before it's uploaded as an artifact.
7. Once you've done that, head over to the Actions tab, and run **Actions -> Set up Reponomics dashboard -> Run workflow**.

The setup workflow asks for:

- README dashboard: `disabled` or `enabled`
- GitHub Pages dashboard: `encrypted-and-published`,
  `plaintext-and-published`, `encrypted-but-NOT-published`,
  `plaintext-but-NOT-published`, or `disabled`

The private default for public repositories is encrypted Pages plus encrypted
Actions artifacts. Choose plaintext output only if you are comfortable exposing
the dashboard data in the deployed dashboard.

## Token

`TRAFFIC_TOKEN` is used to read GitHub traffic, write setup changes, and manage
GitHub Pages for hosted dashboard modes. A classic personal access token with
`repo` scope is the most reliable option when you want private repositories or
hosted Pages. If you only care about public repositories and do not want hosted
Pages, `public_repo` may be sufficient.

Create a token from your GitHub user settings, then save it in this repository
under **Settings -> Secrets and variables -> Actions**.

## Dashboard Key

Encrypted mode uses `TRAFFIC_DASHBOARD_SECRET` to encrypt the dashboard payload
and, when needed, the retained traffic artifact. Generate a long random value
with a password manager and store it somewhere private.

See [Secure Dashboard Key Generation](docs/SECURE_DASHBOARD_KEY.md) for
non-CLI options and rotation guidance.

## Configuration

Edit [config.yaml](config.yaml) to choose which repositories are tracked.

```yaml
max_repos: 50

include:
  - owner/important-repo

exclude:
  - owner/noisy-repo

include_others: true
include_new: false
include_private: true
```

If `include_only` is non-empty, Reponomics tracks exactly those repositories
and ignores the automatic pool.

## After Setup

Setup enables `.github/workflows/collect.yml` and, when README or Pages output
is selected, `.github/workflows/publish.yml`. It does not collect or publish
traffic data immediately. Collection runs twice daily on `main`; publish runs
after successful collection and can also be run manually.

For hosted Pages modes, setup configures GitHub Pages to publish from the
Reponomics publish workflow.

More details are in [docs/README.md](docs/README.md).
