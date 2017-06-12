#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from pprint import pprint
from common import *

reload(sys)
sys.setdefaultencoding("utf8")

theses = load_json("theses.json")

RECORDED_FACULTIES = [FACULTY_MFF_CUNI,
  FACULTY_FIT_BUT,
  FACULTY_FI_MUNI,
  FACULTY_FIT_CTU,
  FACULTY_FELK_CTU,
  unicode(FACULTY_FEI_VSB),
  FACULTY_FAI_UTB,
  FACULTY_PEF_MENDELU,
  FACULTY_UC]

YEAR_RANGE = range(1990,2018)

FACULTY_GRADE_AVERAGES = [
    FACULTY_FIT_BUT,
    FACULTY_FI_MUNI,
    FACULTY_FELK_CTU,
    FACULTY_FAI_UTB,
    FACULTY_MFF_CUNI,
    FACULTY_UC,
    FACULTY_PEF_MENDELU
  ]

DEGREE_SCORES = {
  DEGREE_DOC: 3.0,
  DEGREE_PROF: 3.7,
  DEGREE_CSC: 2.5,
  DEGREE_THD: 2.1,
  DEGREE_DIPLING: 1.6,
  DEGREE_DIS: 0.5,
  DEGREE_DR: 2.1,
  DEGREE_MBA: 2.0
  }

for d in DEGREES_BC:
  DEGREE_SCORES[d] = 1.0

for d in DEGREES_MASTER:
  DEGREE_SCORES[d] = 1.7

for d in DEGREES_DR:
  DEGREE_SCORES[d] = 2.1

for d in DEGREES_PHD:
  DEGREE_SCORES[d] = 2.5

def table_row(cells,cell_width=20):
  result = ""

  for cell in cells:
    result += str(cell).ljust(cell_width)

  return result

def degree_score(person):
  if person == None or not "degrees" in person:
    return 0.0

  result = 0.0

  for d in person["degrees"]:
    if d in DEGREE_SCORES:
      result += DEGREE_SCORES[d]
    else:
      result += 0.1

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
        "greatest degree score person": None,

        "longest abstract thesis": None,
        "shortest abstract thesis": None,
        "most keywords thesis": None,

        "largest thesis": None,
        "smallest thesis": None,

        "grade average male" : (0.0,0),    # (sum,count)
        "grade average female": (0.0,0),

        "oldest thesis": None,

        LANGUAGE_CS: 0,
        LANGUAGE_EN: 0,
        LANGUAGE_SK: 0,
        "unknown language": 0,

        SYSTEM_WORD: 0,
        SYSTEM_OPEN_OFFICE: 0,
        SYSTEM_LATEX: 0,
        SYSTEM_GHOSTSCRIPT: 0,
        "system unknown": 0
      }

    for faculty in RECORDED_FACULTIES:
      self.records[faculty] = 0

    for faculty in FACULTY_GRADE_AVERAGES:
      self.records["grade average " + faculty] = (0.0,0) 

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

    def print_heading(heading_string):
      print("\n~~~~~ " + heading_string + " ~~~~~\n")

    print_heading("faculties")
    cell_width = 17
    faculty_sums = [self.records[f] for f in RECORDED_FACULTIES]
    faculty_sums.append( len( filter(lambda item: not item["faculty"] in RECORDED_FACULTIES,theses)))
    print("  " + table_row( RECORDED_FACULTIES + ["other","total"],cell_width ) )
    print("  " + table_row( faculty_sums + [len(theses)],cell_width ))

    print_heading("gender")
    cell_width = 16
    print("  " + table_row( ["male","female","unknown"],cell_width ))
    print("  " + table_row( [self.records["male"],self.records["female"],self.records["total"] - self.records["male"] - self.records["female"]], cell_width ))

    print_heading("degrees")
    cell_width = 16
    degrees = [DEGREE_BC, DEGREE_ING, DEGREE_MGR, DEGREE_PHD, DEGREE_DOC, DEGREE_RNDR]
    degree_sums = [self.records[d] for d in degrees]
    print("  " + table_row( degrees,cell_width) )
    print("  " + table_row( degree_sums,cell_width) )

    print_heading("grades")
    cell_width = 17
    print("  " + table_row(ALL_GRADES + ["failed"],cell_width))
    print("  " + table_row([self.records[g] for g in ALL_GRADES] + [self.records["not defended"]],cell_width))

    print("\n  average grade (1 = A, 4 = F) by group:")
    groups = FACULTY_GRADE_AVERAGES + ["male","female"]
    averages = []

    for group in groups:
      item = self.records["grade average " + group]
      averages.append("{0:.2f}".format(item[0] / item[1]) if item[1] != 0 else "N/A")

    print("  " + table_row(groups,cell_width))
    print("  " + table_row(averages,cell_width))

    print_heading("years")
    cell_width = 6
    female_male_ratios = ["{0:.2f}".format(float(self.records[str(y) + " female"]) / float(self.records[str(y) + " male"] + 0.0001)) for y in YEAR_RANGE]

    print("  year:        " + table_row(YEAR_RANGE,cell_width))
    print("  total:       " + table_row([self.records[r] for r in YEAR_RANGE],cell_width))
    print("  female/male: " + table_row(female_male_ratios,cell_width))

    print_heading("languages")
    cell_width = 10
    languages = [LANGUAGE_CS,LANGUAGE_SK,LANGUAGE_EN]
    print("  " + table_row(languages + ["unknown"],cell_width))
    print("  " + table_row([self.records[l] for l in languages] + [self.records["unknown language"]],cell_width))

    print_heading("other")

    def print_record(title, lines):
      print(" -- " + title + ": " + lines[0])
 
      if len(lines) > 1:
        for line in lines[1:]:
          print("    " + line)

      print("")

    print_record("longest title (cs)", ["",thesis_to_string(self.records["longest title cs thesis"])])
    print_record("longest title (en)", ["",thesis_to_string(self.records["longest title en thesis"],lang="en")])
    print_record("shortest title (cs)", ["",thesis_to_string(self.records["shortest title cs thesis"])])
    print_record("shortest title (en)", ["",thesis_to_string(self.records["shortest title en thesis"],lang="en")])
    print_record("most pages", [thesis_to_string(self.records["most pages thesis"])]) 
    print_record("least pages", [thesis_to_string(self.records["least pages thesis"])])
    print_record("oldest thesis",[thesis_to_string(self.records["oldest thesis"])])

    print_record("typesetting systems",["",
      "MS Word: " + str(self.records[SYSTEM_WORD]),
      "Open/Libre Office: " + str(self.records[SYSTEM_OPEN_OFFICE]),
      "LaTeX: " + str(self.records[SYSTEM_LATEX]),
      "ghostscript: " + str(self.records[SYSTEM_GHOSTSCRIPT]),
      "unknown: " + str(self.records["system unknown"])])

    print_record("largest thesis", [thesis_to_string(self.records["largest thesis"])])
    print_record("smallest thesis", [thesis_to_string(self.records["smallest thesis"])])

    keywords = [k for k in self.records if type(k) is unicode and starts_with(k,"keyword ")]
    keyword_histogram = sorted([(k[8:],self.records[k]) for k in keywords],key = lambda item: -1 * item[1])

    print_record("most common keywords",[""] + map(lambda item: item[0] + " (" + str(item[1]) + ")",keyword_histogram[:5]))

    field_histogram = sorted([(f,self.records["field " + f]) for f in ALL_FIELDS],key = lambda item: -1 * item[1])

    print_record("most common fields (estimated)",[""] + map(lambda item: item[0] + " (" + str(item[1]) + ")",field_histogram[:5]))

    print_record("person with most degrees", [person_to_string(self.records["most degrees person"])])
    
    print_record("person with greatest degree score", [person_to_string(self.records["greatest degree score person"])])

    print_record("most keywords", [
        thesis_to_string(self.records["most keywords thesis"]),
        "keywords (" + str(len(self.records["most keywords thesis"]["keywords"])) + "): " + ", ".join(self.records["most keywords thesis"]["keywords"])
       ])
 
    if self.records["longest abstract thesis"] != None:
      print_record("longest abstract",[thesis_to_string(self.records["longest abstract thesis"]),self.records["longest abstract thesis"]["abstract_cs"]])
    else:
      print_record("longest abstract",["unresolved"])    

    if self.records["longest abstract thesis"] != None:
      print_record("shortest abstract",[thesis_to_string(self.records["shortest abstract thesis"]),self.records["shortest abstract thesis"]["abstract_cs"]])
    else:
      print_record("shortest abstract",["unresolved"])    

stats = Stats(theses)

thesis_no = 0

for thesis in theses:
  try:
    stats.try_increment("total")
    stats.try_increment(thesis["kind"])

    stats.try_increment(thesis["year"])

    if thesis["language"] == None:
      stats.try_increment("unknown language")
    else:
      stats.try_increment(thesis["language"])

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

    if thesis["grade"] != None:
      if thesis["author"] != None and thesis["author"]["sex"] != None:
        key_string = "grade average " + thesis["author"]["sex"]
        current = stats.records[key_string]
        stats.records[key_string] = (current[0] + grade_to_number(thesis["grade"]), current[1] + 1)

      if thesis["faculty"] in FACULTY_GRADE_AVERAGES:
        key_string = "grade average " + thesis["faculty"]
        current = stats.records[key_string]
        stats.records[key_string] = (current[0] + grade_to_number(thesis["grade"]), current[1] + 1)
        
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

    if thesis["abstract_cs"] != None:
      if stats.records["longest abstract thesis"] == None or len(thesis["abstract_cs"]) > len(stats.records["longest abstract thesis"]["abstract_cs"]):
        stats.records["longest abstract thesis"] = thesis 

      if stats.records["shortest abstract thesis"] == None or len(thesis["abstract_cs"]) < len(stats.records["shortest abstract thesis"]["abstract_cs"]):
        stats.records["shortest abstract thesis"] = thesis 

    if stats.records["most keywords thesis"] == None or len(thesis["keywords"]) > len(stats.records["most keywords thesis"]["keywords"]):
      stats.records["most keywords thesis"] = thesis

    if thesis["year"] != None:
      if stats.records["oldest thesis"] == None or thesis["year"] < stats.records["oldest thesis"]["year"]:
        stats.records["oldest thesis"] = thesis

    people = []

    if thesis["author"] != None:
      people.append(thesis["author"])
    
    if thesis["supervisor"] != None:
      people.append(thesis["supervisor"])

    people += thesis["opponents"]

    for person in people:
      if stats.records["most degrees person"] == None or len(person["degrees"]) > len(stats.records["most degrees person"]["degrees"]):
        stats.records["most degrees person"] = person

      score = degree_score(person)

      if stats.records["greatest degree score person"] == None or score > degree_score(stats.records["greatest degree score person"]):
        stats.records["greatest degree score person"] = person

  except Exception as e:
    print("error analysing thesis no. " + str(thesis_no) + ": " + str(e))
    traceback.print_exc(file=sys.stdout)
 
  thesis_no += 1

stats.nice_print()

