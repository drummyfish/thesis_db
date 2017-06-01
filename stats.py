#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from pprint import pprint
from make_db import *

reload(sys)
sys.setdefaultencoding("utf8")

db_text = get_file_text("theses.json")
theses = json.loads(db_text,encoding="utf8")

YEAR_RANGE = range(1985,2018)

def table_row(cells,cell_width=20):
  result = ""

  for cell in cells:
    result += str(cell).ljust(cell_width)

  return result

class Stats(object):

  def __init__(self):
    self.records = {
        "total": 0,
        THESIS_BACHELOR: 0,
        THESIS_MASTER: 0,
        THESIS_PHD: 0,
        THESIS_DR: 0,
        THESIS_DOC: 0,
  
        FACULTY_MFF_CUNI: 0,
        FACULTY_FIT_BUT: 0,
        FACULTY_FI_MUNI: 0,
        FACULTY_FELK_CTU: 0,
        unicode(FACULTY_FEI_VSB): 0,
        FACULTY_FIT_CTU: 0,
        FACULTY_FAI_UTB: 0,
        FACULTY_PEF_MENDELU: 0,
        FACULTY_UC: 0,
        FACULTY_MVSO: 0,
        FACULTY_FBMI_CTU: 0,
        FACULTY_FD_CTU: 0,
        FACULTY_FJFI_CTU: 0,
        FACULTY_FSV_CTU: 0,

        "male": 0,
        "female": 0,

        "longest title cs": "",
        "longest title en": "",
        "shortest title cs": "                                      ",
        "shortest title en": "                                      "
      }

    for degree in DEGREES:
      self.records[degree] = 0

    for year in YEAR_RANGE:
      self.records[year] = 0

  def try_increment(self, key):
    if key in self.records:
      self.records[key] += 1
      return True

    return False

  def nice_print(self):
    print("================= thesis DB stats ================ ")

    print("faculties:")
    faculties = [FACULTY_FIT_BUT, FACULTY_FI_MUNI, FACULTY_MFF_CUNI, FACULTY_FELK_CTU, FACULTY_FAI_UTB, unicode(FACULTY_FEI_VSB), FACULTY_PEF_MENDELU, FACULTY_UC, FACULTY_MVSO]
    faculty_sums = [self.records[f] for f in faculties]
    faculty_sums.append( len( filter(lambda item: not item["faculty"] in faculties,theses)))
    print(table_row( faculties + ["other","total"] ,16) )
    print(table_row( faculty_sums + [len(theses)] ,16 ))
    print("")    

    print("degrees:")
    degrees = [DEGREE_BC, DEGREE_ING, DEGREE_MGR, DEGREE_PHD, DEGREE_DOC, DEGREE_RNDR, DEGREE_PHDR]
    degree_sums = [self.records[d] for d in degrees]
    print(table_row( degrees ,16) )
    print(table_row( degree_sums ,16) )
    print("")

    print("years:")
    print(table_row(YEAR_RANGE,5))
    print("")

    print("records:")

    print("longest title (cs): " + str(self.records["longest title cs"]))
    print("longest title (en): " + str(self.records["longest title en"]))
    print("shortest title (cs): " + str(self.records["shortest title cs"]))
    print("shortest title (en): " + str(self.records["shortest title en"]))


stats = Stats()

thesis_no = 0

for thesis in theses:
  try:
    stats.try_increment("total")
    stats.try_increment(thesis["kind"])
    stats.try_increment(thesis["year"])
    stats.try_increment(thesis["faculty"])
    stats.try_increment(thesis["degree"])
  
    if thesis["title_cs"] != None and len(thesis["title_cs"]) > len(stats.records["longest title cs"]):
      stats.records["longest title cs"] = thesis["title_cs"] 
 
    if thesis["title_en"] != None and len(thesis["title_en"]) > len(stats.records["longest title en"]):
      stats.records["longest title en"] = thesis["title_en"] 

    if thesis["title_cs"] != None and len(thesis["title_cs"]) > 0 and len(thesis["title_cs"]) < len(stats.records["shortest title cs"]):
      print("sasas")
      stats.records["shortest title cs"] = thesis["title_cs"] 
 
    if thesis["title_en"] != None and len(thesis["title_en"]) > 0 and len(thesis["title_en"]) < len(stats.records["shortest title en"]):
      stats.records["shortest title en"] = thesis["title_en"] 

    try:
      stats.try_increment(thesis["author"]["sex"])
    except Exception:
      pass
  except Exception as e:
    print("error analysing thesis no. " + str(thesis_no) + ": " + str(e))
    traceback.print_exc(file=sys.stdout)
 
  thesis_no += 1

stats.nice_print()
  
  
    


