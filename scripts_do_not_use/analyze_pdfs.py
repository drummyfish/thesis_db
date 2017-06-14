#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

sys.path.insert(0,"../tools")

from theses_common import *

INPUT_FILE = "../theses.json"
OUTPUT_FILE = "theses_pdf_updated.json"
END_AFTER = 200

theses = load_json(INPUT_FILE)

def thesis_needs_pdf_analysis(thesis):
  return thesis["pages"] == None or thesis["typesetting_system"] == None or thesis["size"] == None or thesis["language"] == None

for i in range(len(theses)):
#for i in range(END_AFTER):
#  print(i)

  try:
    #random_index = random.randint(0,len(theses) - 1)
    random_index = i

    random_thesis = theses[random_index]

    if random_thesis["kind"] == THESIS_PHD and random_thesis["url_fulltext"] != None and thesis_needs_pdf_analysis(random_thesis):

    #if random_thesis["url_fulltext"] != None and thesis_needs_pdf_analysis(random_thesis):
      print(i,"chosen: " + thesis_to_string(random_thesis))

      
      print("needs PDF update")

      pdf_info = download_and_analyze_pdf(random_thesis["url_fulltext"])

      print(pdf_info.pages,pdf_info.typesetting_system,pdf_info.size,pdf_info.language)

      if random_thesis["pages"] == None:
        random_thesis["pages"] = pdf_info.pages

      if random_thesis["typesetting_system"] == None:
        random_thesis["typesetting_system"] = pdf_info.typesetting_system

      if random_thesis["size"] == None:
        random_thesis["size"] = pdf_info.size

      if random_thesis["language"] == None:
        if pdf_info.language in LANGUAGES:
          random_thesis["language"] = pdf_info.language
      
  except Exception as e:
    print("ERROR: " + str(e))

print("saving...")
save_json(theses,OUTPUT_FILE)
