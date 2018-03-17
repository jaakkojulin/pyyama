#!/bin/bash
echo -e "<!DOCTYPE RCC><RCC version=\"1.0\">\n<qresource prefix=\"icons\">" > icons.qrc
for file in icons32/*.png icons128/*.png iconssvg/*.svg; do echo "    <file>$file</file>" >> icons.qrc; done
echo -e "</qresource>\n</RCC>" >> icons.qrc
pyrcc5 -o icons_rc.py icons.qrc
pyuic5 -o pyyamamainwindow.py pyyamamainwindow.ui
