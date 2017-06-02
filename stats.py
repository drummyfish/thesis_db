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

  result = ""

  degrees_after = []

  for degree in person["degrees"]:
    if degree in DEGREES_AFTER:
      degrees_after.append(degree)
    else:
      result += degree + " "

  result += str(person["name_first"]) + " " + str(person["name_last"])

  for degree in degrees_after:
    result += " " + degree

  return result

def thesis_to_string(thesis, lang="cs"):
  if thesis == None:
    return "none"

  result = ""

  if thesis["author"] != None:
    result += person_to_string(thesis["author"]) + ": "

  other_lang = "en" if lang == "cs" else "cs"

  result += str(thesis["title_" + lang] if thesis["title_" + lang] != None else thesis["title_" + other_lang])

  if thesis["year"] != None:
    result += ", " + str(thesis["year"])

  if thesis["faculty"] != None:
    result += ", " + thesis["faculty"]

  if thesis["kind"] != None:
    result += ", " + thesis["kind"] + " thesis"

  if thesis["pages"] != None:
    result += ", " + str(thesis["pages"]) + " pages"

  if thesis["size"] != None:
    result += ", " + "{0:.2f}".format(thesis["size"] / 1000000.0) + " MB"

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

        "longest title cs thesis": None,
        "longest title en thesis": None,
        "shortest title cs thesis": None,
        "shortest title en thesis": None,
        "most pages thesis": None,
        "least pages thesis": None,
        "most degrees person": None,

        "largest thesis": None,
        "smallest thesis": None,

        SYSTEM_WORD: 0,
        SYSTEM_OPEN_OFFICE: 0,
        SYSTEM_LATEX: 0,
        "system unknown": 0
      }

    for degree in DEGREES:
      self.records[degree] = 0

    for year in YEAR_RANGE:
      self.records[year] = 0
      self.records[str(year) + " male"] = 0
      self.records[str(year) + " female"] = 0

    for field in ALL_FIELDS:
      self.records["field " + field] = 0

  def try_increment(self, key):
    if key in self.records:
      self.records[key] += 1
      return True

    return False

  def do_increment(self, key):
    if key in self.records:
      self.records[key] += 1
      return True
    
    self.records[key] = 1
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

    print("\nother:")
    print("  longest title (cs): " + thesis_to_string(self.records["longest title cs thesis"]))
    print("  longest title (en): " + thesis_to_string(self.records["longest title en thesis"],lang="en"))
    print("  shortest title (cs): " + thesis_to_string(self.records["shortest title cs thesis"]))
    print("  shortest title (en): " + thesis_to_string(self.records["shortest title en thesis"],lang="en"))
    print("  most pages: " + thesis_to_string(self.records["most pages thesis"])) 
    print("  least pages: " + thesis_to_string(self.records["least pages thesis"]))
    print("  typesetting systems: ")
    print("    MS Word: " + str(self.records[SYSTEM_WORD]))
    print("    Open/Libre Office: " + str(self.records[SYSTEM_OPEN_OFFICE]))
    print("    LaTeX: " + str(self.records[SYSTEM_LATEX]))
    print("    unknown: " + str(self.records["system unknown"]))

    print("  largest thesis: " + thesis_to_string(self.records["largest thesis"]))
    print("  smallest thesis: " + thesis_to_string(self.records["smallest thesis"]))

    keywords = [k for k in self.records if type(k) is unicode and starts_with(k,"keyword ")]
    keyword_histogram = sorted([(k[8:],self.records[k]) for k in keywords],key = lambda item: -1 * item[1])

    print("  most common keywords: ")

    for k in keyword_histogram[:5]:
      print("    " + k[0] + " (" + str(k[1]) + ")")

    field_histogram = sorted([(f,self.records["field " + f]) for f in ALL_FIELDS],key = lambda item: -1 * item[1])

    print("  most common field (estimated): ")

    for f in field_histogram[:5]:
      print("    " + f[0] + " (" + str(f[1]) + ")")

    print("  person with most degrees: " + person_to_string(self.records["most degrees person"]))

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

    if thesis["typesetting_system"] != None:
      stats.try_increment(thesis["typesetting_system"])
    else:
      stats.try_increment("system unknown")

    for keyword in thesis["keywords"]:
      stats.do_increment("keyword " + keyword.lower())

    if thesis["field"] != None: 
      stats.try_increment("field " + thesis["field"])

    if thesis["defended"] == False:
      stats.try_increment("not defended")

    def title_length_helper(lang, thesis, longest):
      helper_str = "longest" if longest else "shortest"

      if thesis["title_" + lang] != None:
        if stats.records[helper_str + " title " + lang + " thesis"] == None:
          stats.records[helper_str + " title " + lang + " thesis"] = thesis 
        else:
          comparison = len(thesis["title_" + lang]) > len(stats.records[helper_str + " title " + lang + " thesis"]["title_" + lang])
          
          if not longest:
            comparison = not comparison

          if comparison:
            stats.records[helper_str + " title " + lang + " thesis"] = thesis 
 
    title_length_helper("cs",thesis,True)
    title_length_helper("cs",thesis,False)
    title_length_helper("en",thesis,True)
    title_length_helper("en",thesis,False)

    try:
      stats.try_increment(thesis["author"]["sex"])
    except Exception:
      pass

    if thesis["size"] != None:
      if stats.records["largest thesis"] == None or thesis["size"] > stats.records["largest thesis"]["size"]:
        stats.records["largest thesis"] = thesis

      if stats.records["smallest thesis"] == None or thesis["size"] < stats.records["smallest thesis"]["size"]:
        stats.records["smallest thesis"] = thesis

    people = []

    if thesis["author"] != None:
      people.append(thesis["author"])
    
    if thesis["supervisor"] != None:
      people.append(thesis["supervisor"])

    people += thesis["opponents"]

    for person in people:
      if stats.records["most degrees person"] == None or len(person["degrees"]) > len(stats.records["most degrees person"]["degrees"]):
        stats.records["most degrees person"] = person

  except Exception as e:
    print("error analysing thesis no. " + str(thesis_no) + ": " + str(e))
    traceback.print_exc(file=sys.stdout)
 
  thesis_no += 1

stats.nice_print()
#pprint(stats.records)  
  
    

