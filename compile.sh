#!/bin/bash -e

cd "$(dirname ${BASH_SOURCE[0]})"

for i in ui/*.ui; do
	name=$(basename $i .ui)
	echo $name.ui
	pyside2-uic $i -o src/ui/$name.py
done
