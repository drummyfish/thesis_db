# Czech Computer Science Thesis Database

This is a (still work-in-progress) JSON DB of university theses written in the Czech Republic.

These theses are usually freely available at university websites, but each of these websites has
a different interface, shows different info in different formats, allows limited searching etc.
This project aims to make a unified database for students and teachers to easily see which
topics have been covered in the huge area of computer science.

# Important Notes

  - Sometimes some information is unavailable online, the crawler can make
    mistakes due to bugs, wrong estimations etc., so don't take the
    info in the DB for granted, double check everything.

  - The DB is not and probably will never be completed.

  - The Python scripts, especially `make_db.py`, do not work out of the box
    and shouldn't be just run. Also the code is ugly as it's not meant to be reusable.
    The code is here mostly for reference, so do not run it.

# Info and Interesting Statistics

Some interesting statistics gathered so far (for more see `stats.txt`).

- **total**: 36127 theses (31872 male, 2654 female, 1601 unknown)
- **faculties analyzed**:  FIT BUT, FI MUNI, MFF CUNI, FAI UTB, FEI VŠB, FIT CTU, FELK CTU, PEF MENDELU, Unicorn College, FACULTY_FBMI_CTU, FACULTY_FD_CTU, FACULTY_FJFI_CTU, FACULTY_FSV_CTU
- **longest title (yes, it's a title)**: Navrhněte a ve VRML naplementujte systém pro 3-D internetovou galerii, která umožní tvorbu virtuálních výstav libovolných uměleckých děl. Následná internetová aplikace umožní do galerie vkládat libovolné 2-D i 3-D modely uměleckých děl a tím realizovat vlastní výstavy.
- **shortest title**: Risk, 2013 MFF CUNI bachelor's thesis
- **longest abstract**: 6813 characters (to read see `stats.txt`), 2005 master's thesis at FELK CTU
- **shortest abstract**: NIC, failed thesis at FIT BUT from 2012
- **most common keywords**: PHP (1159), Java (1108), MySQL (878), informační systém (688), databáze (610)
- **most common field (estimated)**: computer graphics
- **oldest thesis**: year 1983, Modelování sémantiky programovacích jazyků a využití modelů při implementaci programovacích jazyků, PhD thesis of Ing. Tomáš Hruška
- **most keywords**: 281, 2006 FIT BUT bachelor's thesis

- **degrees**:

  |Bc.  |Ing.|Mgr.|PhD.|doc.|RNDr|
  |-----|----|----|----|----|----|
  |18638|7116|4617|956 |58  |334 |

- **grades**:

  |A    |B   |C   |D   |E   |F   |FIT BUT avg.|MFF CUNI avg.|FAI UTB avg.|male avg.|female avg.|
  |-----|----|----|----|----|----|------------|-------------|------------|---------|-----------|
  |4353 |2810|2177|828 |525 |309 |1.81        |1.42         |1.48        |1.63     |1.49       |

- **female/male ratio by year**:

  |1992|1995|2000|2005|2010|2015|
  |----|----|----|----|----|----|
  |0   |0.23|0.06|0.07|0.07|0.14|
  
- **languages**:

  |cs   |sk  |en  |unknown|
  |-----|----|----|-------|
  |25333|2350|3090|5354   |

# Format

In the repository here, the DB is stored in JSON that is compressed
(no whitechars or empty attributes) to not waste space. The file is
named `theses_compressed.json`.

It is more convenient and sometimes (for the tools in this repo)
required to uncompress the JSON (so that the object have all the
attributes, set to `null` if unknown). This can be done with
`uncompress_json.py`.

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

In any way you want. This repo, however, offers some tools you may find useful:

- `inspect.html`: Simple HTML viewer that allows for advanced search, sorting etc. Tested only in Chrome.
- `stats.py`: Computes the statistics of the database (see above).