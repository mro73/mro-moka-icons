#!/usr/bin/python3
#
# Original script by Sam Hewitt (Moka Icon Theme)
# Modified in 2026 by mro73
#
# Renders the source SVGs (one icon per SVG, sizes marked by "Baseplate" rects)
# into PNGs, in one of two folder layouts:
#
#   --layout moka  ->  <out>/16x16/apps/name.png, <out>/16x16@2x/apps/name.png ...
#                      (default out: <repo>/mro-moka-icons)
#   --layout mint  ->  <out>/apps/16/name.png,  <out>/apps/16@2x/name.png ...
#                      (default out: ../Mint-L-mro, next to this repo)
#
# Examples (can be run from any directory):
#   ./render-bitmaps.py                         render everything, Moka layout
#   ./render-bitmaps.py -l mint                 render everything into Mint-L-mro
#   ./render-bitmaps.py -l mint steam           re-render only S/steam.svg
#   ./render-bitmaps.py -l mint -o /tmp/test    render somewhere else
#   ./render-bitmaps.py -f                      re-render even if PNGs are up to date
#
# --- Original Legal Stuff ---
#
# This file is part of the Moka Icon Theme and is free software; you can
# redistribute it and/or modify it under  the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation; version 3.
#
# This file is part of the Moka Icon Theme and is distributed in the hope that
# it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, see <https://www.gnu.org/licenses/lgpl-3.0.txt>
#
#
# Thanks to the GNOME icon developers for the original version of this script

import argparse
import os
import shutil
import subprocess
import sys
import xml.sax

INKSCAPE = shutil.which('inkscape') or '/usr/bin/inkscape'
OPTIPNG = shutil.which('optipng')

# Paths are based on where this script lives, not where you run it from.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))     # .../src/bitmaps
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..'))

DEFAULT_OUT = {
    'moka': os.path.join(REPO_ROOT, 'mro-moka-icons'),
    'mint': os.path.join(REPO_ROOT, '..', 'Mint-L-mro'),
}

SOURCES = ('#', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
           'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'web')

DPI_1_TO_1 = 96     # resolution of normal (non-HiDPI) icons
DPIS = [1, 2]       # render at 1x and 2x


def output_dir(layout, out, context, width, height, scale):
    """Folder a PNG goes into, depending on the chosen layout."""
    suffix = f'@{scale}x' if scale != 1 else ''
    if layout == 'moka':
        return os.path.join(out, f'{width}x{height}{suffix}', context)
    return os.path.join(out, context, f'{width}{suffix}')


def needs_render(svg, png, force):
    return force or not os.path.exists(png) or os.path.getmtime(svg) > os.path.getmtime(png)


def render(svg, rect_id, dpi, png):
    subprocess.run([INKSCAPE, svg,
                    f'--export-id={rect_id}',
                    f'--export-dpi={dpi}',
                    f'--export-filename={png}'], check=True)
    if OPTIPNG:
        subprocess.run([OPTIPNG, '-quiet', '-o7', png], check=True)


class IconCollector(xml.sax.ContentHandler):
    """Reads one SVG and collects (context, icon name, size rects) per Baseplate layer."""
    ROOT, SVG, LAYER, OTHER, TEXT = range(5)

    def __init__(self):
        super().__init__()
        self.stack = [self.ROOT]
        self.inside = [self.ROOT]
        self.icons = []
        self.chars = ''
        self.text = None

    def _push(self, state):
        self.stack.append(state)
        self.inside.append(state)

    def startElement(self, name, attrs):
        top = self.inside[-1]
        if top == self.ROOT and name == 'svg':
            self._push(self.SVG)
            return
        if (top == self.SVG and name == 'g'
                and attrs.get('inkscape:groupmode') == 'layer'
                and attrs.get('inkscape:label', '').startswith('Baseplate')):
            self._push(self.LAYER)
            self.context = None
            self.icon_name = None
            self.rects = []
            return
        if top == self.LAYER:
            label = attrs.get('inkscape:label')
            if name == 'text' and label in ('context', 'icon-name'):
                self._push(self.TEXT)
                self.text = label
                self.chars = ''
                return
            if name == 'rect':
                self.rects.append({'id': attrs['id'],
                                   'width': attrs['width'],
                                   'height': attrs['height']})
        self.stack.append(self.OTHER)

    def endElement(self, name):
        stacked = self.stack.pop()
        if self.inside[-1] == stacked:
            self.inside.pop()
        if stacked == self.TEXT and self.text:
            if self.text == 'context':
                self.context = self.chars
            else:
                self.icon_name = self.chars
            self.text = None
        elif stacked == self.LAYER:
            if not (self.context and self.icon_name):
                raise ValueError('Baseplate layer is missing its "context" or "icon-name" text')
            self.icons.append((self.context, self.icon_name, self.rects))

    def characters(self, chars):
        self.chars += chars.strip()


def process_svg(svg, args, out):
    collector = IconCollector()
    with open(svg) as f:
        xml.sax.parse(f, collector)

    force = args.force or bool(args.svg)     # naming one SVG always re-renders it
    for context, icon_name, rects in collector.icons:
        if args.filter is not None and icon_name not in args.filter:
            continue
        print(context, icon_name)
        for rect in rects:
            width = int(float(rect['width']))
            height = int(float(rect['height']))
            for scale in DPIS:
                folder = output_dir(args.layout, out, context, width, height, scale)
                os.makedirs(folder, exist_ok=True)
                png = os.path.join(folder, icon_name + '.png')
                if needs_render(svg, png, force):
                    render(svg, rect['id'], DPI_1_TO_1 * scale, png)
                    sys.stdout.write('.')
                else:
                    sys.stdout.write('-')
                sys.stdout.flush()
        print()


def main():
    parser = argparse.ArgumentParser(description='Render icons from SVG to PNG')
    parser.add_argument('svg', nargs='?', metavar='SVG',
                        help='SVG name (without .svg) to render; if omitted, render all icons')
    parser.add_argument('filter', nargs='?', metavar='FILTER',
                        help='only render icon names matching this, inside the given SVG')
    parser.add_argument('-l', '--layout', choices=['moka', 'mint'], default='moka',
                        help='folder layout of the output (default: moka)')
    parser.add_argument('-o', '--out',
                        help='output folder (default depends on --layout)')
    parser.add_argument('-f', '--force', action='store_true',
                        help='re-render even if PNGs are newer than their SVGs')
    args = parser.parse_args()

    if not os.path.exists(INKSCAPE):
        sys.exit('Inkscape not found.')
    if not OPTIPNG:
        print('Note: optipng not found, PNGs will not be optimized.')

    out = os.path.abspath(args.out or DEFAULT_OUT[args.layout])
    print(f'Layout: {args.layout}   Output: {out}\n')

    for source in SOURCES:
        src_dir = os.path.join(SCRIPT_DIR, source)
        if not os.path.isdir(src_dir):
            continue
        if args.svg:
            names = [args.svg + '.svg'] if os.path.exists(os.path.join(src_dir, args.svg + '.svg')) else []
        else:
            names = sorted(n for n in os.listdir(src_dir) if n.endswith('.svg'))
        for name in names:
            process_svg(os.path.join(src_dir, name), args, out)


if __name__ == '__main__':
    main()
