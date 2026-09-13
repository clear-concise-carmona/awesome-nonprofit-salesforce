# Contributing

## Submission criteria

An entry qualifies if it's:

1. **Open source** - public repo, real license, not a marketing page for a paid product.
2. **Nonprofit-Salesforce-relevant** - built for or heavily used on NPSP, Nonprofit Cloud, Agentforce Nonprofit, or a nonprofit-specific workflow (grants, gift processing, volunteer management, program delivery). General Salesforce tooling only qualifies if nonprofits specifically rely on it and there's no nonprofit-specific alternative (see the AI & Agentforce category for examples - that space doesn't have nonprofit-specific tooling yet, so general Agentforce SDKs are listed with that caveat stated inline).
3. **Actually inspectable** - a real repo with real commits, not a placeholder or a repo that just exists to link out to a paid product.

## What doesn't qualify

- Vendor landing pages, even if the vendor also has open-source components elsewhere.
- Repos with unverified claims about who uses them ("used by 500+ nonprofits!") and no way to check.
- Duplicate entries - if a project's canonical repo already has an entry, don't add a fork unless the fork is now the maintained version (and you can show that).

## How to submit

Open a PR that adds an entry to `data/entries.yml` under the right category, then run:

```
pip install -r scripts/requirements.txt
python scripts/generate_readme.py
```

and commit the regenerated `README.md` along with your YAML change. The `validate-readme-sync.yml` workflow will fail your PR if the two are out of sync.

Include in your PR description:

- What the project does, one sentence.
- Why it's nonprofit-Salesforce-relevant if that's not obvious from the name.
- Whether you're affiliated with the project (disclose it - see how CCC's own entries are marked with `maintainer:` in the YAML).

## About the staleness flags

`docs/STATUS.md` is regenerated weekly and flags entries with no push in 18+ months as "may be unmaintained," and flags anything GitHub reports as archived. Flags don't get an entry removed automatically. Reasons an entry stays despite a flag:

- It's finished, stable, and doesn't need commits to keep working (a lot of admin-facing declarative tools are like this).
- It's still the only option in its category, flag or not - a flagged tool beats no tool, as long as you know what you're getting into.

If you think a flagged entry should actually be removed (abandoned, broken, superseded by something better), open an issue and say why, rather than assuming the flag alone is enough.
