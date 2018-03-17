#!/bin/bash
#    Copyright (C) 2018 Jaakko Julin
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    See file "LICENSE" for details.
echo -e "<!DOCTYPE RCC><RCC version=\"1.0\">\n<qresource prefix=\"icons\">" > icons.qrc
for file in icons32/*.png icons128/*.png iconssvg/*.svg; do echo "    <file>$file</file>" >> icons.qrc; done
echo -e "</qresource>\n</RCC>" >> icons.qrc
pyrcc5 -o icons_rc.py icons.qrc
pyuic5 -o pyyamamainwindow.py pyyamamainwindow.ui
