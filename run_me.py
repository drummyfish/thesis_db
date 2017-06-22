import sys

sys.path.insert(0,"./tools")

import decompress_json
decompress_json.do_main(["","theses_compressed.json"])
import make_thesis_list
import make_csv
