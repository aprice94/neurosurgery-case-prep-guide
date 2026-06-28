---
title: "Custom Domains Setup"
description: "DNS records and GitHub Pages settings for Pterion Prep and CraniPro."
category: "Resources"
tags:
  - "domain"
  - "DNS"
  - "GitHub Pages"
---

# Custom Domains Setup

The repository is configured for **pterionprep.com** with a root `CNAME` file and Jekyll metadata pointing at `https://pterionprep.com`.

## Pterion Prep

At the domain registrar or DNS host for `pterionprep.com`, add these records:

| Host | Type | Value |
| --- | --- | --- |
| `@` | `A` | `185.199.108.153` |
| `@` | `A` | `185.199.109.153` |
| `@` | `A` | `185.199.110.153` |
| `@` | `A` | `185.199.111.153` |
| `www` | `CNAME` | `aprice94.github.io` |

Then in GitHub: repository **Settings -> Pages -> Custom domain** should be `pterionprep.com`; after DNS verifies, enable **Enforce HTTPS**.

## CraniPro

`cranipro.com` should be a separate site or a registrar-level/domain-host redirect, because GitHub Pages supports one primary custom domain per repository.

Fastest working setup:

| Host | Type | Value |
| --- | --- | --- |
| `@` | URL redirect | `https://pterionprep.com/cranipro/` |
| `www` | URL redirect | `https://pterionprep.com/cranipro/` |

Cleaner standalone setup:

1. Publish CraniPro from its own public repository or a dedicated static host.
2. Add a root `CNAME` file containing `cranipro.com` in that CraniPro site.
3. Point `cranipro.com` DNS to that host.
4. Keep the CraniPro back link pointed to `https://pterionprep.com/`.

## Notes

- DNS propagation can take minutes to 24 hours.
- Do not enable a domain in GitHub Pages until the DNS records resolve, or the old GitHub Pages URL may redirect to a domain that is not live yet.
- The current Pterion Prep repo can publish `https://pterionprep.com/cranipro/`; `https://cranipro.com` needs DNS redirect or a separate Pages site.
