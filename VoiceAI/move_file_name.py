#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path
import shutil
import re

source_path = "/home/data_ok/"
target_path = "/home/data_ok/"


for path in Path(source_path).glob("*"):

    file_name = "%s" % path.name
    path = "%s" % path

    new_path = re.sub(r"[\W]", "_", file_name)

    new_path = "%s%s" % (target_path, new_path)

    shutil.move(path, new_path)
