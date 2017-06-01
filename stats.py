#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from pprint import pprint
from make_db import *

with open("theses.json") as data_file:    
  theses = json.load(data_file)

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
        FACULTY_FEI_VSB: 0,
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
      }

    for year in range(1980,2020):
      self.records[year] = 0

  def try_increment(self, key):
    if key in self.records:
      self.records[key] += 1
      return True

    return False

  def nice_print(self):
    pass
    # todo

stats = Stats()

for thesis in theses:
  stats.try_increment("total")
  stats.try_increment(thesis["kind"])
  stats.try_increment(thesis["year"])
  stats.try_increment(thesis["faculty"])
  
  try:
    stats.try_increment(thesis["author"]["sex"])
  except Exception:
    pass
  

  
  
    


pprint(stats.records)
