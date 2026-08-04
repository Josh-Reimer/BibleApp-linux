#!/bin/sh
# Builds dist/BibleApp-<version>-<arch>.AppImage
#
# An AppImage has to be self-contained, so — exactly as in the Flatpak — Tcl,
# Tk and CPython are compiled in, because no distro's Python can be assumed to
# ship Tkinter.
#
# Everything is configured with --prefix="$APPDIR/usr" rather than
# --prefix=/usr + DESTDIR. That matters: Python locates Tk through pkg-config,
# and a DESTDIR install writes .pc files claiming prefix=/usr, which would make
# configure link against the *host's* Tk instead of the one just built.
# Absolute paths baked into the binaries are corrected at runtime by AppRun.
#
# Build on the oldest glibc you intend to support — an AppImage produced on
# Ubuntu 24.04 will not start on older distros. CI uses ubuntu-22.04.
set -eu

VERSION="${VERSION:-1.0.0}"
ARCH="${ARCH:-$(uname -m)}"
TCL_VER=8.6.15
TK_VER=8.6.15
PY_VER=3.12.11
PY_MM=3.12

TCL_SHA=861e159753f2e2fbd6ec1484103715b0be56be3357522b858d3cbb5f893ffef1
TK_SHA=550969f35379f952b3020f3ab7b9dd5bfd11c1ef7c9b7c6a75f5c49aca793fec
PY_SHA=7b8d59af8216044d2313de8120bfc2cc00a9bd2e542f15795e1d616c51faf3d6

ROOT=$(cd "$(dirname "$0")/.." && pwd)
WORK="${WORK:-$ROOT/build-appimage}"
APPDIR="$WORK/AppDir"
OUT="${OUT:-$ROOT/dist}"
SRC="$WORK/src"
JOBS=$(nproc 2>/dev/null || echo 2)

mkdir -p "$SRC" "$APPDIR/usr" "$OUT"

get() {
    url=$1; sha=$2; f="$SRC/$(basename "$url")"
    [ -f "$f" ] || curl -fsSL -o "$f" "$url"
    echo "$sha  $f" | sha256sum -c - >/dev/null
    tar xf "$f" -C "$SRC"
}

TCLTK_BASE=https://downloads.sourceforge.net/project/tcl/Tcl/$TCL_VER
get "$TCLTK_BASE/tcl$TCL_VER-src.tar.gz" "$TCL_SHA"
get "$TCLTK_BASE/tk$TK_VER-src.tar.gz"   "$TK_SHA"
get "https://www.python.org/ftp/python/$PY_VER/Python-$PY_VER.tgz" "$PY_SHA"

echo "==> tcl"
cd "$SRC/tcl$TCL_VER/unix"
./configure --prefix="$APPDIR/usr" --enable-threads --enable-64bit >/dev/null
make -j"$JOBS" >/dev/null && make install >/dev/null
find "$APPDIR/usr/lib" -name '*.so' -exec chmod u+w {} +

echo "==> tk"
cd "$SRC/tk$TK_VER/unix"
./configure --prefix="$APPDIR/usr" --with-tcl="$APPDIR/usr/lib" \
            --enable-threads --enable-64bit >/dev/null
make -j"$JOBS" >/dev/null && make install >/dev/null
find "$APPDIR/usr/lib" -name '*.so' -exec chmod u+w {} +

echo "==> python"
cd "$SRC/Python-$PY_VER"
PKG_CONFIG_PATH="$APPDIR/usr/lib/pkgconfig" \
    ./configure --prefix="$APPDIR/usr" --enable-shared --with-ensurepip=no \
                LDFLAGS="-Wl,-rpath,\$ORIGIN/../lib" >/dev/null
make -j"$JOBS" >/dev/null && make install >/dev/null

# Same gate as the Flatpak: refuse to package a Python that cannot open a window.
LD_LIBRARY_PATH="$APPDIR/usr/lib" "$APPDIR/usr/bin/python3" -c "import tkinter"

rm -rf "$APPDIR/usr/lib/python$PY_MM/test" \
       "$APPDIR/usr/lib/python$PY_MM/idlelib" \
       "$APPDIR/usr/lib/python$PY_MM/lib2to3"

echo "==> app"
install -d "$APPDIR/usr/share/bibleapp" \
           "$APPDIR/usr/share/applications" \
           "$APPDIR/usr/share/icons/hicolor/256x256/apps" \
           "$APPDIR/usr/share/metainfo"
install -m644 "$ROOT"/*.py "$APPDIR/usr/share/bibleapp/"
find "$ROOT" -maxdepth 1 -name '*.txt' ! -name 'bibleSearchResult.txt' \
     -exec install -m644 {} "$APPDIR/usr/share/bibleapp/" \;

# Shared with the Flatpak and .deb builds; see packaging/build-deb.sh.
DESKTOP=io.github.josh_reimer.BibleApp.desktop
install -m644 "$ROOT/flatpak/$DESKTOP" "$APPDIR/usr/share/applications/"
install -m644 "$ROOT/flatpak/io.github.josh_reimer.BibleApp.metainfo.xml" \
              "$APPDIR/usr/share/metainfo/"
install -m644 "$ROOT/black-bible.png" \
              "$APPDIR/usr/share/icons/hicolor/256x256/apps/io.github.josh_reimer.BibleApp.png"

# appimagetool wants the desktop entry and icon at the AppDir root too.
install -m644 "$ROOT/flatpak/$DESKTOP" "$APPDIR/$DESKTOP"
install -m644 "$ROOT/black-bible.png" "$APPDIR/io.github.josh_reimer.BibleApp.png"
cp "$ROOT/black-bible.png" "$APPDIR/.DirIcon"

# PYTHONHOME retargets the interpreter's baked-in build prefix; LD_LIBRARY_PATH
# and TCL/TK_LIBRARY point Tcl at its script library inside the mounted image.
cat > "$APPDIR/AppRun" <<EOF
#!/bin/sh
HERE=\$(dirname "\$(readlink -f "\$0")")
export PYTHONHOME="\$HERE/usr"
export LD_LIBRARY_PATH="\$HERE/usr/lib\${LD_LIBRARY_PATH:+:\$LD_LIBRARY_PATH}"
export TCL_LIBRARY="\$HERE/usr/lib/tcl$TCL_VER"
export TK_LIBRARY="\$HERE/usr/lib/tk$TK_VER"
exec "\$HERE/usr/bin/python3" "\$HERE/usr/share/bibleapp/bible-gui-tk.py" "\$@"
EOF
chmod 755 "$APPDIR/AppRun"

echo "==> appimagetool"
TOOL="$WORK/appimagetool-$ARCH.AppImage"
[ -f "$TOOL" ] || curl -fsSL -o "$TOOL" \
    "https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-$ARCH.AppImage"
chmod 755 "$TOOL"

# No FUSE on CI runners, so unpack the tool instead of mounting it.
cd "$WORK"
APPIMAGE_EXTRACT_AND_RUN=1 ARCH="$ARCH" "$TOOL" \
    "$APPDIR" "$OUT/BibleApp-$VERSION-$ARCH.AppImage"

echo "built $OUT/BibleApp-$VERSION-$ARCH.AppImage"
