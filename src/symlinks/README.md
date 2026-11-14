## Symbolic Links

Some apps don't need a new drawing, just a different name for an icon that already exists. Instead of copying files, the theme uses symbolic links, listed per `context` in [bitmaps](./bitmaps) (`apps.list`, later maybe `places.list` etc.).

Each line in a list is:

```
<existing-icon>  <new-name>
```

For example `TiddlyDesktop.png org.tiddlywiki.TiddlyDesktop.png`.

`<existing-icon>` can be:

- **one of our own icons** – the link is relative, inside the theme;
- **an icon from the parent theme (Mint-L)** – the link points to `/usr/share/icons/Mint-L/...`. Use this when you want an app to show an icon Mint-L already has.

Our own icons are checked first. Lines starting with `#` are comments.

### [generate-symlinks.sh](./generate-symlinks.sh)

```
./generate-symlinks.sh                                     # Mint-L-mro next to this repo, parent Mint-L
./generate-symlinks.sh ~/path/to/Mint-L-mro                # another theme folder
./generate-symlinks.sh ~/path/to/Mint-Y-mro /usr/share/icons/Mint-Y
```

- Removes all old links in the theme first, so a deleted line also removes its link. Drawn PNGs are never touched.
- Reports lines whose icon can't be found anywhere.
- Run it again after rendering new icons, so links to them are created too.
