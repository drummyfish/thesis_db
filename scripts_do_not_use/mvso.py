import sys

sys.path.insert(0,"../tools")

from make_db import *
import theses_common

mvso = MvsoDownloader()

theses = []

for i in range(1,81):
  theses.append(mvso.get_thesis_info("../mvso theses/" + str(i) + ".html"))

theses_common.save_json(theses,"mvso.json")

