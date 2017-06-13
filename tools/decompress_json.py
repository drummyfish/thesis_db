import theses_common
import sys

def decompress(theses, output_filename):  # makes the json big and readable again
  def decompressed_person(person):
    if person == None:
      return

    for word in ["name_first","name_last","sex"]:
      if not word in person:
        person[word] = None

    if not "degrees" in person:
      person["degrees"] = []

  reference_thesis = theses_common.Thesis()

  decompressed = []

  for thesis in theses:
    new_thesis = {}

    for attr in reference_thesis.__dict__:
      new_thesis[attr] = thesis[attr] if attr in thesis else None

    new_thesis["keywords"] = thesis["keywords"] if "keywords" in thesis else []
    new_thesis["opponents"] = thesis["opponents"] if "opponents" in thesis else []

    decompressed_person(new_thesis["author"])
    decompressed_person(new_thesis["supervisor"])

    for opponent in new_thesis["opponents"]:
      decompressed_person(opponent)

    decompressed.append(new_thesis)

  theses_common.save_json(decompressed,output_filename)

def do_main(argv):
  print("loading DB from " + argv[1])
  theses = theses_common.load_json(argv[1])
  new_filename = argv[1].replace("_compressed.json",".json")
  print("decompressing to " + new_filename)
  decompress(theses, new_filename)
  print("done")

if __name__ == "__main__":

  if len(sys.argv) != 2:
    print("error: expecting one argument: json file to compress")
  else:
    do_main(sys.argv)
