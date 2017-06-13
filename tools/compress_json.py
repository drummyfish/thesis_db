import theses_common
import sys
import json

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

def compress(theses, output_filename):  # make the json small, dropping empty characters and null properties
  f = open(output_filename,"w")
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

def do_main(argv):
  print("loading DB from " + argv[1])
  theses = theses_common.load_json(sys.argv[1])
  new_filename = argv[1].replace(".json","_compressed.json")
  print("compressing to " + new_filename)
  compress(theses, new_filename)
  print("done")

if __name__ == "__main__":
  if len(sys.argv) != 2:
    print("error: expecting one argument: json file to compress")
  else:
    do_main(sys.argv)
