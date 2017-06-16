import sys

sys.path.insert(0,"../tools")

import theses_common

theses = theses_common.load_json("../theses.json")

for thesis in theses:
  if thesis["title_cs"] == None and thesis["title_en"] == None:
    print(thesis)
