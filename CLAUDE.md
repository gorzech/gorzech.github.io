# CLAUDE.md — gorzech.github.io (PUBLIC repo)

Greg's personal website (gregdynamics.com), built with Quarto and published to GitHub Pages.

- Everything here is public. Nothing confidential: no partner, funding, unpublished or hiring details.
- Pushing to `main` publishes the site (`.github/workflows/publish.yml` renders to `gh-pages`). Ask Greg before any push.
- Shared wording comes from the `atoms` submodule. Change it in the atoms repo, then update it here with `git submodule update --remote atoms`. Do not edit files inside `atoms/`.
- Publications: edit `publications.bib` only. `scripts/gen_publications.py` writes `generated/` (ignored by git) before each render.
- Checks before calling something done: `make test`, `make check`, then `make render` (or `make preview`). `make pubs-pdf` builds the publications PDF and needs TinyTeX.
- Decks rendered from other repos go in `talks/` only.
