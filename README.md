# gorzech.github.io

Personal website of Grzegorz Orzechowski, built with [Quarto](https://quarto.org/) and published to [GitHub Pages](https://pages.github.com/).

## Project layout

- `index.qmd`: main pages
- `styles.css`: site styles
- `_quarto.yml`: site configuration
- `content/`: submodule with shared content (e.g., `content/profiles/greg.md`)

## Local preview

```bash
quarto preview
```

## Publish

GitHub Actions renders and publishes the site to `gh-pages`. You can also publish manually:

```bash
quarto publish gh-pages
```

## Submodule setup

This repo uses a `content` submodule. Initialize it after cloning:

```bash
git submodule update --init --recursive
```
