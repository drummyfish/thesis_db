import theses_common
import sys
import json

INPUT_FILE = "theses.json"
OUTPUT_COMPRESSED_FILE = "theses_compressed.json"

def remove_empty_attributes(json_object):
  if not type(json_object) is dict:
    return json_object

  result = {}

  for attribute in json_object:
    item = json_object[attribute]

    if item == None:
      pass
    elif type(item) is list:
      if len(item) > 0:
        result[attribute] = [remove_empty_attributes(i) for i in item]
    elif type(item) is dict:
      result[attribute] = remove_empty_attributes(item)
    else:
      result[attribute] = item      

  return result

def compress():    # make the json small, dropping empty characters and null properties
  print("compressing...")

  f = open(OUTPUT_COMPRESSED_FILE,"w")
  f.write("[")

  first = True

  for thesis in theses:   # keep one thesis per line for git friendliness
    if first:
      first = False
    else:
      f.write(",\n")

    line = json.dumps(remove_empty_attributes(thesis),sort_keys=True,ensure_ascii=False,separators=(",",":"))
    f.write(line)

  f.write("\n]")
  f.close()

theses = theses_common.load_json(INPUT_FILE) 
compress()
