#!/bin/bash
#
# Description:
#   Creates icon aliases (symbolic links) in the Mint-L-mro theme from the
#   list files in ./bitmaps/<context>.list
#
#   Each line in a list file is:   <existing-icon> <new-name>
#   e.g.                           steam_icon_40970.png  some-other-name.png
#
#   For every size folder, the script links <new-name> to:
#     1. our own icon, if <existing-icon> exists in our theme (relative link), or
#     2. the parent theme's icon (default /usr/share/icons/Mint-L), if it exists there.
#   Lines whose target exists in neither place are reported and skipped.
#
#   All old symlinks in the theme are removed first, so deleting a line from a
#   list removes its link on the next run. Your drawn PNGs are never touched.
#
# Usage:
#   ./generate-symlinks.sh                                   default paths
#   ./generate-symlinks.sh ~/path/to/Mint-L-mro              other theme folder
#   ./generate-symlinks.sh ~/path/to/Mint-Y-mro /usr/share/icons/Mint-Y
#
# Based on generate-symlinks.sh from the Moka Icon Theme by Sam Hewitt.
# Modified in 2026 by mro73.
#
# Legal Stuff:
#
# This script is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; version 3.
#
# This script is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, see <https://www.gnu.org/licenses/gpl-3.0.txt>

DIR=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )

THEME_DIR=$(realpath -m "${1:-$DIR/../../../Mint-L-mro}")
PARENT_DIR=$(realpath -m "${2:-/usr/share/icons/Mint-L}")

SIZES=("16" "22" "24" "32" "48" "64" "96" "256"
       "16@2x" "22@2x" "24@2x" "32@2x" "48@2x" "64@2x" "96@2x" "256@2x")

if [ ! -d "$THEME_DIR" ]; then
	echo "Theme folder not found: $THEME_DIR"
	exit 1
fi
if [ ! -d "$PARENT_DIR" ]; then
	echo "Parent theme not found: $PARENT_DIR"
	exit 1
fi

echo "Theme:  $THEME_DIR"
echo "Parent: $PARENT_DIR"

echo "Removing old links..."
find "$THEME_DIR" -type l -delete

made=0
problems=0

for LIST in "$DIR"/bitmaps/*.list; do
	[ -e "$LIST" ] || continue
	CONTEXT=$(basename "$LIST" .list)
	echo " -- $CONTEXT"

	while read -r TARGET LINK _; do
		# skip empty lines and comments
		[[ -z "$TARGET" || "$TARGET" == \#* ]] && continue
		if [ -z "$LINK" ]; then
			echo "    !! line with only one name: $TARGET"
			problems=$((problems + 1))
			continue
		fi

		found=0
		for SIZE in "${SIZES[@]}"; do
			DEST="$THEME_DIR/$CONTEXT/$SIZE"
			OURS="$DEST/$TARGET"
			THEIRS="$PARENT_DIR/$CONTEXT/$SIZE/$TARGET"

			if [ -e "$OURS" ]; then
				ln -sfn "$TARGET" "$DEST/$LINK"
			elif [ -e "$THEIRS" ]; then
				mkdir -p "$DEST"
				ln -sfn "$THEIRS" "$DEST/$LINK"
			else
				continue
			fi
			found=1
			made=$((made + 1))
		done

		if [ "$found" -eq 0 ]; then
			echo "    !! $TARGET not found in theme or parent (wanted for $LINK)"
			problems=$((problems + 1))
		fi
	done < "$LIST"
done

echo "Done: $made links created, $problems problem(s)."
