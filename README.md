# Czech Computer Science Thesis Database

This is a (still work-in-progress) JSON DB of computer science university theses written in the Czech Republic, made
with Python 2.7.

These theses are usually freely available at university websites, but each of these websites has
a different interface, shows different info in different formats, allows limited searching etc.
This project aims to make a unified database for students and teachers to easily see which
topics have been covered in the huge area of computer science.

![screenshot](https://github.com/drummyfish/thesis_db/blob/master/screenshot.png?raw=true)

# Important Notes

  - Sometimes some information is unavailable online, the crawler can make
    mistakes due to bugs, wrong estimations etc., so don't take the
    info in the DB for granted, double check everything.

  - The DB is not and probably will never be completed.

  - The Python scripts in `scripts_do_not_use` do not work out of the box
    and shouldn't be just run. Also the code is ugly as it's not meant to be reusable.
    The code is here mostly for reference, so do not run it.

# Info and Interesting Statistics

Some interesting statistics gathered so far (for more see `stats.txt`).

- **total**: 39871 theses (35626 male, 3185 female, 1060 unknown)
- **faculties analyzed**:  FIT BUT, FI MUNI, MFF CUNI, FAI UTB, FEI VŠB, FIT CTU, FELK CTU, PEF MENDELU, Unicorn College, FBMI CTU, FD CTU, FJFI CTU, FSV CTU, MVŠO, FEEC BUT, FME BUT
- **longest title (yes, it's a title)**: Navrhněte a ve VRML naplementujte systém pro 3-D internetovou galerii, která umožní tvorbu virtuálních výstav libovolných uměleckých děl. Následná internetová aplikace umožní do galerie vkládat libovolné 2-D i 3-D modely uměleckých děl a tím realizovat vlastní výstavy.
- **shortest title (cs)**: Risk, 2013 MFF CUNI bachelor's thesis
- **shortest title (en)**: IS, 2005 FIT BUT bachelor's thesis
- **least pages and defended**: Optimalizace v zadní části zpětného překladače, 2013 FIT BUT bachelor thesis, 21 pages (conclusion at page 14), grade: A
- **most pages**: Řízení systémů se zpožděním - Algebraický přístup, 2007 FAI UTB PhD thesis, 324 pages
- **longest abstract**: 6813 characters (to read see `stats.txt`), 2005 master's thesis at FELK CTU
- **shortest abstract**: NIC, failed thesis at FIT BUT from 2012
- **shortest abstract and defended**: Microsoft Azure výhody a nevýhody služby, 2014 FAI UTB bachelor thesis (the abstract is same as title)
- **most common keywords**: PHP (1247), Java (1234), MySQL (944), informační systém (703), databáze (660)
- **most common field (estimated)**: computer graphics
- **oldest thesis**: Jan Honzík's 1966 master thesis
- **most keywords**: 281, 2006 FIT BUT bachelor's thesis
- **total PDF pages analyzed**: 154237

- **degrees**:

  |Bc.  |Ing.|Mgr.|PhD.|doc.|RNDr|
  |-----|----|----|----|----|----|
  |20658|8807|4617|964 |68  |335 |

- **grades**:

  |A    |B   |C   |D   |E   |F   |FIT BUT avg.|MFF CUNI avg.|FAI UTB avg.|male avg.|female avg.|
  |-----|----|----|----|----|----|------------|-------------|------------|---------|-----------|
  |4451 |2905|2236|832 |527 |309 |1.81        |1.42         |1.48        |1.63     |1.49       |

- **female/male ratio by year**:

  |1990|1994|2000|2005|2010|2015|
  |----|----|----|----|----|----|
  |0   |0.02|0.06|0.07|0.07|0.15|
  
- **languages**:

  |cs   |sk  |en  |unknown|
  |-----|----|----|-------|
  |29021|2676|3334|4840   |

- **typesetting systems**:

  |Word|Open Office|LaTeX|ghostscript|unknown|
  |----|-----------|-----|-----------|-------|
  |735 |181        |748  |18         |37611  |

# Format

In the repository here, the DB is stored in JSON that is compressed
(no whitechars or empty attributes) to not waste space. It is still a
valid JSON. The file is named `theses_compressed.json`.

It is more convenient and sometimes (for the tools in this repo)
required to decompress the JSON (so that the object have all the
attributes, set to `null` if unknown). This can be done with
`decompress_json.py`.

The database is a JSON list consisting of objects in format:

```
  FIELD               POSSIBLE VALUES           EXPLANATION

{
  title_en:           String, null              title in English
  title_cs:           String, null              title in Czech
  language:           "cs", "sk", "en", null    primary language
  keywords:           [String]                  keywords
  year:               Number, null              completion year
  city:               String, null              city
  kind:               "bachelor","master",      type
                      "PhD","habilitation",
                      "small doctorate", null
  degree:             String, null              awarded degree
  faculty:            String, null              faculty abbreviation
  department:         String, null              depratment abbreviation
  url_page:           String, null              URL of thesis webpage
  url_fulltext:       String, null              URL of fulltext
  author:             Person, null              thesis author
  supervisor:         Person, null              thesis supervisor
  grade:              "A", "B", "C", "D",       final grade
                      "E", "F", null
  defended:           Boolean, null             whether defended
  pages:              Number, null              number of fulltext pages
  typesetting_system: "LaTeX", "Open Office",   typesetting system used
                      "MS Word", "ghostscript"
                      "typewriter", "other",
                      null
  opponents:          [Person]                  thesis opponents
  field:              String, null              estimated field
  abstract_cs:        String, null              abstract in Czech
  abstract_en:        String, null              abstract in English
  size:               Number, null              size in bytes
  public_university:  Boolean, null             public/private uni
  branch:             String, null              branch of study
  note:               String, null              possible note
}
```

where Person is another JSON object:

```
{
  name_first:         String, null              person first name
  name_last:          String, null              person last name
  degrees:            [String]                  list of degrees
  sex:                "male", "female", null    estimated sex/gender
}
```
# How to Work With the Database

In any way you want, it's JSON. Firstly run `run_me.py` though, as it uncompresses the JSON etc.

This repo offers some tools you may find useful, located in the `tools` folder
(I'm still working on these so don't expect them to work perfectly):

- `run_me.py`: Decompresses the DB to `theses.json` file, makes a plain-text list of theses and CSV format database (delimited with `|`).
- `inspect.html`: Simple HTML viewer that allows for advanced search, sorting etc. Tested only in Chrome. This tool should be suitable to most people for quick searches and inspections.
- `stats.py`: Computes the statistics of the database (see above).
- `theses_common.py`: Common stuff you may find useful when working with the DB from within Python.
