#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from pprint import pprint
from make_db import *

reload(sys)
sys.setdefaultencoding("utf8")

db_text = get_file_text("theses.json")
theses = json.loads(db_text,encoding="utf8")

YEAR_RANGE = range(1990,2018)

def table_row(cells,cell_width=20):
  result = ""

  for cell in cells:
    result += str(cell).ljust(cell_width)

  return result

def person_to_string(person):
  if person == None:
    return "none"

  return str(person["name_first"]) + " " + str(person["name_last"])

def thesis_to_string(thesis):
  if thesis == None:
    return "none"

  result = ""

  if thesis["author"] != None:
    result += person_to_string(thesis["author"]) + ": "

  result += str(thesis["title_cs"] if thesis["title_cs"] != None else thesis["title_en"])

  if thesis["year"] != None:
    result += ", " + str(thesis["year"])

  if thesis["faculty"] != None:
    result += ", " + thesis["faculty"]

  if thesis["kind"] != None:
    result += ", " + thesis["kind"] + " thesis"

  if thesis["pages"] != None:
    result += ", " + str(thesis["pages"]) + " pages"

  return result

class Stats(object):

  def __init__(self, thesis_list):
    self.thesis_list = thesis_list

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

        GRADE_A: 0,
        GRADE_B: 0,
        GRADE_C: 0,
        GRADE_D: 0,
        GRADE_E: 0,
        GRADE_F: 0,

        "not defended": 0,

        "male": 0,
        "female": 0,

        "longest title cs": "",
        "longest title en": "",
        "shortest title cs": "                                      ",
        "shortest title en": "                                      ",
        "most pages thesis": None,
        "least pages thesis": None
      }

    for degree in DEGREES:
      self.records[degree] = 0

    for year in YEAR_RANGE:
      self.records[year] = 0
      self.records[str(year) + " male"] = 0
      self.records[str(year) + " female"] = 0

  def try_increment(self, key):
    if key in self.records:
      self.records[key] += 1
      return True

    return False

  def nice_print(self):
    print("================= thesis DB stats ================ ")

    print("\nfaculties:")
    cell_width = 16
    faculties = [FACULTY_FIT_BUT, FACULTY_FI_MUNI, FACULTY_MFF_CUNI, FACULTY_FELK_CTU, FACULTY_FAI_UTB, unicode(FACULTY_FEI_VSB), FACULTY_PEF_MENDELU, FACULTY_UC, FACULTY_MVSO]
    faculty_sums = [self.records[f] for f in faculties]
    faculty_sums.append( len( filter(lambda item: not item["faculty"] in faculties,theses)))
    print("  " + table_row( faculties + ["other","total"],cell_width ) )
    print("  " + table_row( faculty_sums + [len(theses)],cell_width ))

    print("\ngender:")
    cell_width = 16
    print("  " + table_row( ["male","female","unknown"],cell_width ))
    print("  " + table_row( [self.records["male"],self.records["female"],self.records["total"] - self.records["male"] - self.records["female"]], cell_width ))

    print("\ndegrees:")
    cell_width = 16
    degrees = [DEGREE_BC, DEGREE_ING, DEGREE_MGR, DEGREE_PHD, DEGREE_DOC, DEGREE_RNDR, DEGREE_PHDR]
    degree_sums = [self.records[d] for d in degrees]
    print("  " + table_row( degrees,cell_width) )
    print("  " + table_row( degree_sums,cell_width) )

    print("\ngrades:")
    cell_width = 8
    print("  " + table_row(ALL_GRADES + ["failed"],cell_width))
    print("  " + table_row([self.records[g] for g in ALL_GRADES] + [self.records["not defended"]],cell_width))

    print("\nyears:")
    cell_width = 6
    female_male_ratios = ["{0:.2f}".format(float(self.records[str(y) + " female"]) / float(self.records[str(y) + " male"] + 0.0001)) for y in YEAR_RANGE]

    print("  year:        " + table_row(YEAR_RANGE,cell_width))
    print("  total:       " + table_row([self.records[r] for r in YEAR_RANGE],cell_width))
    print("  female/male: " + table_row(female_male_ratios,cell_width))

    print("\nrecords:")
    print("  longest title (cs): " + str(self.records["longest title cs"]))
    print("  longest title (en): " + str(self.records["longest title en"]))
    print("  shortest title (cs): " + str(self.records["shortest title cs"]))
    print("  shortest title (en): " + str(self.records["shortest title en"]))


    print("  most pages: " + thesis_to_string(self.records["most pages thesis"])) 
    print("  least pages: " + thesis_to_string(self.records["least pages thesis"]))
    print("  most common keywords: ")
    print("  most common field (estimated): ")
    print("  person with most degrees: ")

stats = Stats(theses)

thesis_no = 0

for thesis in theses:
  try:
    stats.try_increment("total")
    stats.try_increment(thesis["kind"])

    stats.try_increment(thesis["year"])

    try:
      stats.try_increment(str(thesis["year"]) + " " + thesis["author"]["sex"])
    except Exception as e:
      pass

    if thesis["pages"] != None:
      if stats.records["most pages thesis"] == None or thesis["pages"] > stats.records["most pages thesis"]["pages"]:
        stats.records["most pages thesis"] = thesis

      if stats.records["least pages thesis"] == None or thesis["pages"] < stats.records["least pages thesis"]["pages"]:
        stats.records["least pages thesis"] = thesis

    stats.try_increment(thesis["faculty"])
    stats.try_increment(thesis["degree"]) 
    stats.try_increment(thesis["grade"])

    if thesis["defended"] == False:
      stats.try_increment("not defended")

    if thesis["title_cs"] != None and len(thesis["title_cs"]) > len(stats.records["longest title cs"]):
      stats.records["longest title cs"] = thesis["title_cs"] 
 
    if thesis["title_en"] != None and len(thesis["title_en"]) > len(stats.records["longest title en"]):
      stats.records["longest title en"] = thesis["title_en"] 

    if thesis["title_cs"] != None and len(thesis["title_cs"]) > 0 and len(thesis["title_cs"]) < len(stats.records["shortest title cs"]):
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
#pprint(stats.records)  
  
    

