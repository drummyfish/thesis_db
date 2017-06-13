import theses_common

input_filename = "theses.json"
output_filename = "thesis_list.txt"

theses = theses_common.load_json(input_filename)

output_file = open(output_filename,"w")

print("writing plain text thesis list to " + output_filename)

for thesis in theses:
  output_file.write(theses_common.thesis_to_string(thesis) + "\n")

output_file.close()
