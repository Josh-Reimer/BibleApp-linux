#!/bin/sh
# Builds dist/bibleapp_<version>_all.deb
#
# The package is Architecture: all — there is nothing to compile. It depends on
# the distro's python3-tk rather than bundling Tk, which is what keeps it a few
# megabytes instead of the ~16 MB the Flatpak needs.
set -eu

VERSION="${VERSION:-1.0.0}"
MAINTAINER="${MAINTAINER:-Josh Reimer <98061271+Josh-Reimer@users.noreply.github.com>}"

ROOT=$(cd "$(dirname "$0")/.." && pwd)
OUT="${OUT:-$ROOT/dist}"
STAGE=$(mktemp -d)
trap 'rm -rf "$STAGE"' EXIT

install -d "$STAGE/DEBIAN" \
           "$STAGE/usr/bin" \
           "$STAGE/usr/share/bibleapp" \
           "$STAGE/usr/share/applications" \
           "$STAGE/usr/share/icons/hicolor/256x256/apps" \
           "$STAGE/usr/share/metainfo" \
           "$OUT"

# Program files. bibleSearchResult.txt is a stray runtime output file that may
# be sitting in the working tree; it is not part of the app.
install -m644 "$ROOT"/*.py "$STAGE/usr/share/bibleapp/"
find "$ROOT" -maxdepth 1 -name '*.txt' ! -name 'bibleSearchResult.txt' \
     -exec install -m644 {} "$STAGE/usr/share/bibleapp/" \;

cat > "$STAGE/usr/bin/bibleapp" <<'EOF'
#!/bin/sh
exec /usr/bin/python3 /usr/share/bibleapp/bible-gui-tk.py "$@"
EOF
chmod 755 "$STAGE/usr/bin/bibleapp"

# The desktop entry, icon, and metainfo are shared with the Flatpak build;
# flatpak/ is where they live because the manifest needs them under those exact
# names. Exec=bibleapp and Icon=<app id> are equally valid outside a sandbox.
install -m644 "$ROOT/flatpak/io.github.josh_reimer.BibleApp.desktop" \
              "$STAGE/usr/share/applications/"
install -m644 "$ROOT/flatpak/io.github.josh_reimer.BibleApp.metainfo.xml" \
              "$STAGE/usr/share/metainfo/"
install -m644 "$ROOT/black-bible.png" \
              "$STAGE/usr/share/icons/hicolor/256x256/apps/io.github.josh_reimer.BibleApp.png"

INSTALLED_KB=$(du -ks "$STAGE" | cut -f1)

cat > "$STAGE/DEBIAN/control" <<EOF
Package: bibleapp
Version: $VERSION
Section: education
Priority: optional
Architecture: all
Depends: python3 (>= 3.8), python3-tk
Maintainer: $MAINTAINER
Homepage: https://github.com/Josh-Reimer/BibleApp-linux
Installed-Size: $INSTALLED_KB
Description: Desktop Bible reader with search
 A simple GUI Bible program for navigating to any book, chapter or verse and
 searching the text. The complete King James Version is bundled, so it works
 with no network connection.
 .
 Supports whole-word search, searching a single testament or the current book,
 four themes, and an adjustable reading font.
EOF

# --root-owner-group avoids needing fakeroot or a root build.
dpkg-deb --build --root-owner-group "$STAGE" \
         "$OUT/bibleapp_${VERSION}_all.deb"

echo "built $OUT/bibleapp_${VERSION}_all.deb"
