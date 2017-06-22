import theses_common

DELIMITER = "|"

input_filename = "theses.json"
output_filename = "theses.csv"

theses = theses_common.load_json(input_filename)

output_file = open(output_filename,"w")

print("making CSV file to " + output_filename)

def to_csv(what):
  if what == None:
    return ""

  return str(what).replace(DELIMITER,"")

for thesis in theses:
  csv_line = DELIMITER.join(to_csv(item) for item in (
    thesis["title_cs"],
    thesis["title_en"],
    theses_common.person_to_string(thesis["author"]),
    theses_common.person_to_string(thesis["supervisor"]),
    thesis["faculty"],
    thesis["department"],
    thesis["branch"],
    thesis["public_university"],
    thesis["year"],
    thesis["city"],
    thesis["kind"],
    thesis["degree"],
    thesis["grade"],
    thesis["defended"],
    thesis["language"],
    ", ".join(map(lambda o: theses_common.person_to_string(o),thesis["opponents"])),
    ", ".join(thesis["keywords"]),
    thesis["abstract_cs"],
    thesis["abstract_en"],
    thesis["pages"],
    thesis["typesetting_system"],
    thesis["size"],
    thesis["url_page"],
    thesis["url_fulltext"],
    thesis["field"],
    thesis["note"]
    ))

  output_file.write(csv_line + "\n")

output_file.close()
