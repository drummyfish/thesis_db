from common import *
import json

INPUT_FILE = "theses.json"
OUTPUT_COMPRESSED_FILE = "theses_compressed.json"
OUTPUT_UNCOMPRESSED_FILE = "theses.json"

reload(sys)
sys.setdefaultencoding("utf8")
db_text = get_file_text(INPUT_FILE)
theses = json.loads(db_text,encoding="utf8")

def remove_empty_attributes(json_object):
  if not type(json_object) is dict:
    return json_object

  result = {}

  for attribute in json_object:
    item = copy.deepcopy(json_object[attribute])

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
  f = open(OUTPUT_COMPRESSED_FILE,"w")
  f.write("[")

  for thesis in theses:   # keep one thesis per line for git friendliness
    line = json.dumps(remove_empty_attributes(thesis),sort_keys=True,ensure_ascii=False,separators=(",",":")) + ",\n"
    f.write(line)

  f.write("]")
  f.close()

def uncompress():  # makes the json big and readable again
  def uncompressed_person(person):
    if person == None:
      return

    for word in ["name_first","name_last","sex"]:
      if not word in person:
        person[word] = None

    if not "degrees" in person:
      person["degrees"] = []

  f = open(OUTPUT_UNCOMPRESSED_FILE,"w")

  reference_thesis = Thesis()

  uncompressed = []

  for thesis in theses:
    new_thesis = {}

    for attr in reference_thesis.__dict__:
      new_thesis[attr] = thesis[attr] if attr in thesis else None

    new_thesis["keywords"] = thesis["keywords"] if "keywords" in thesis else []
    new_thesis["opponents"] = thesis["opponents"] if "opponents" in thesis else []

    uncompressed_person(new_thesis["author"])
    uncompressed_person(new_thesis["supervisor"])

    for opponent in new_thesis["opponents"]:
      uncompressed_person(opponent)

    uncompressed.append(new_thesis)

  f.write(json.dumps(uncompressed,sort_keys=True,ensure_ascii=False,indent=1))

  f.close()

compress()
uncompress()
