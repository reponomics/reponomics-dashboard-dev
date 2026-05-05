# Reponomics Dashboard

Welcome to your personal GitHub BI dashboard.

Every repo you own is full of data, delivered to you hourly by GitHub itself - view count, unique visitors, clones, top referring sites, and most popular pages. GitHub provides this data to every repo, for free - tucked away in a tab under Insights > Traffic. If you're trying to launch an app, or grow your user base, this data can unlock key metrics that will help you reach your goals, and understand your growth. The problem is it's not so easy to take advantage of that data.

## 1) The 14-Day Window

If you want insights into your repo's traffic over the past 14 days, it's only a few clicks away. But what if you want that _same_ data one month from now. Were you storing it? If not, unfortunately it's gone for good. There's no API to get it from. There's just a rolling 14-day window of insights, and every day the tail of that window disappears. The Reponomics Dashboard allows you start collecting that data _today_. Maybe you're not even sure if you'll want it in one month - but unless you start collecting it now, if you decide you _do_ want to take a look at it, you might have missed your chance.

## 2) A Different Page for Every Repo

Now, suppose you have more than one repo where you have an amazing app and you want to analyze its growth. Well, GitHub is generous enough to give you that 14-day window of data, for all of these repos - but they don't give you a _unified_ window where you can look at all of that data at once. And if you're building more than one app, you probably want to see how they're performing relative to one another. You don't just want to collect the data, you want to aggregate it, and analyze it, and compare it. This template repo allows you to do all of those things, in a clear HTML dashboard. That's pretty cool - but it's not even the cool part.

## Private Data, Public Hosting

There's a reason why the Traffic data that GitHub provides to you is only visible to users with push access to the repository - it's private information. And you might want to keep it that way. Usually, that means if you want to deploy a website where you can view that data and interact with it, you have to find a place to host it. And hosting it usually costs a little bit time, and a little bit of money. Which is a shame because another cool thing about GitHub is they give every repo a free static site hosting option in the form of GitHub Pages, which is very nice of them. The only problem is - whether your repo is public or private, your GitHub Pages site is public.

The Reponomics Dashboard template repo solves this problem for you - public website, private data. When you create a repo based off of this template, you start by setting up a private key. There's a number of ways you can create a key, or a password - the only important thing is to make sure that it's _really, really long_. Once you create your key, you store it somewhere accessible, like your password manager, or your Keychain, and then you save it to the repository as a repo secret. Now you're ready to get going - that's all the setup you need.

The repo is configurable so you can choose to use all these features, some of them, or none. But once you've set up your repo secret, you're ready to start collecting Traffic data from any repository where you have access to it, and it will _never be stored anywhere in plain text_. Twice a day, a workflow will go around to whatever repositories you've configured it to collect from, it will query for that data, write it all down to a CSV file, _encrypt the CSV file_ using your very, very long password, and then upload it as a workflow artifact. The plain text data never lands in your repo's source code. Then, assuming you want that nice HTML dashboard, it will generate the entire dashboard in an encrypted form, and _that's_ what GitHub Pages will serve. Your private dashboard is open to the public - that's true. But it's only served in an encrypted form. Then when you visit the dashboard, if you know the repository secret, you enter that into the password field, and the dashboard is decrypted using strictly client-side decryption.

### It Couldn't Be Any Easier

What's the upshot? Persistent storage of ephemeral data; aggregated across multiple repos; collected and immediately encrypted before it's uploaded as a workflow artifact; and then served via GitHub Pages in encrypted form. All of it for free - no third parties - no external APIs or services - no plaintext data stored anywhere - and all of it is under your control. You decide what to do with the data, whether you want to host it on GitHub Pages, download the dashboard and view it offline, or just keep it stored as an artifact for some future use yet to be determined. As long as you have the repo secret, it's all being aggregated in a CSV file that you can decrypt whenever you decide you want to use it. And if you happen to forget that extremely long password? That's OK too. So long as you have control of the repository's workflows, you can rotate the key any time you want.

#### ***This even works for public repos and free accounts.***

That's what the Reponomics Dashboard template repo offers you - a way to actually _do something_ with all that valuable data that GitHub is sending you, make it last longer than the 14-day expiration date, aggregate it across your repos, and provide you with a turnkey solution for private, encrypted hosting of your analytics dashboard using GitHub's freely provided public infrastructure.

## Quick Setup

1. Create a repository from this template.
2. Add a repository secret named `TRAFFIC_TOKEN`.
3. For encrypted dashboard or encrypted artifact mode, add
   `TRAFFIC_DASHBOARD_SECRET`.
4. Run **Actions -> Set up Reponomics dashboard -> Run workflow**.

The setup workflow asks for:

- README dashboard: `disabled` or `enabled`
- GitHub Pages dashboard: `encrypted`, `plain`, or `disabled`

The private default for public repositories is encrypted Pages plus encrypted
Actions artifacts. Choose plain output only if you are comfortable publishing
the traffic data.

## Token

`TRAFFIC_TOKEN` is used to read GitHub traffic and repository metadata. A
classic personal access token with `repo` scope is the most reliable option
when you want to include private repositories. If you only care about public
repositories, `public_repo` may be sufficient.

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

For hosted Pages, set **Settings -> Pages -> Source** to **Deploy from a
branch**, choose branch `main`, folder `/docs`, then save.

More details are in [docs/README.md](docs/README.md).
