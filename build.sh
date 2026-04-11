#!/usr/bin/env bash
set -euo pipefail

if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "Not using virtualenv."
    exit 1
fi

APP_NAME="Bunny"
ARCH="x86_64"
APPDIR="${APP_NAME}.AppDir"
APPIMAGETOOL="$VIRTUAL_ENV/bin/appimagetool-${ARCH}.AppImage"
APPIMAGETOOL_URL="https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-${ARCH}.AppImage"
OUTPUT="${APP_NAME}-${ARCH}.AppImage"

if [[ ! -f "$APPIMAGETOOL" ]]; then
    echo "Fetching appimagetool..."
    if command -v wget &>/dev/null; then
        wget -q "$APPIMAGETOOL_URL" -O "$APPIMAGETOOL"
    else
        curl -sSL "$APPIMAGETOOL_URL" -o "$APPIMAGETOOL"
    fi
    chmod +x "$APPIMAGETOOL"
fi

rm -rf build dist *.spec

pip install -r requirements.txt
pip install pyinstaller

pyinstaller --onedir --name "$APP_NAME" \
    --icon static/icon.png \
    --add-data "templates:templates" \
    --add-data "static:static" \
    --hidden-import webview \
    --hidden-import webview.platforms.qt \
    --hidden-import qtpy \
    --clean \
    --noconfirm \
    web.py

rm -rf "$APPDIR"
mkdir -p "$APPDIR/usr/bin"

cp -r dist/"$APP_NAME"/* "$APPDIR/usr/bin/"

cat > "$APPDIR/AppRun" << EOF
#!/bin/bash
SELF=\$(readlink -f "\$0")
HERE="\${SELF%/*}"
export LD_LIBRARY_PATH="\$HERE/usr/bin:\${LD_LIBRARY_PATH:-}"
exec "\$HERE/usr/bin/${APP_NAME}" "\$@"
EOF
chmod +x "$APPDIR/AppRun"

cat > "$APPDIR/${APP_NAME}.desktop" << EOF
[Desktop Entry]
Name=${APP_NAME}
Exec=${APP_NAME}
Icon=${APP_NAME}
Type=Application
Categories=Utility;
EOF

ICON_DST="$APPDIR/${APP_NAME}.png"
if [[ -f "static/icon.png" ]]; then
    cp "static/icon.png" "$ICON_DST"
fi

ARCH=$ARCH "$APPIMAGETOOL" "$APPDIR" "$OUTPUT"

bash ./clean.sh