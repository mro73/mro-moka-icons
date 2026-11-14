## Source Files

Don't edit the rendered PNGs directly. Every icon is drawn as an SVG source here and rendered by script.

- [bitmaps](./bitmaps) – SVG sources and the render script for all icons.
- [symlinks](./symlinks) – lists of icon aliases and the script that turns them into symbolic links.

### How-To

1. Draw or edit an icon in `bitmaps/` (start from `Template.svg`).
2. Render it:
   - `bitmaps/render-bitmaps.py` – PNGs in the Moka layout, into `mro-moka-icons/` in this repo.
   - `bitmaps/render-bitmaps.py -l mint` – PNGs in the Linux Mint layout, into the `Mint-L-mro` theme folder next to this repo.
3. If an app needs an extra name, or should reuse an existing Mint-L icon, add a line to `symlinks/bitmaps/<context>.list` and run `symlinks/generate-symlinks.sh`.
