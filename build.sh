#!/usr/bin/env bash

if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "Not using virtualenv."
    exit 1
fi

pip install -r requirements.txt

pip install pyinstaller

rm -rf build dist *.spec
pyinstaller --onefile --name "Bunny" \
	--add-data "templates:templates" \
	--add-data "static:static" \
	--hidden-import webview \
	--hidden-import webview.platforms.qt \
	--hidden-import qtpy \
	--clean \
	--noconfirm \
	web.py
