import theses_common

theses = theses_common.load_json("../theses.json")

print("normalizing")

for i in range(len(theses)):  
  thesis_obj = theses_common.Thesis()
  thesis_obj.from_json_object(theses[i])
  changes_made = thesis_obj.normalize()

  if changes_made:
    print(theses_common.thesis_to_string(theses[i]))
    theses[i] = thesis_obj

theses_common.save_json(theses,"../theses_normalized.json")

print("done")
