THIS IS WORK IN PROGGRESS

CZECH COMPUTER SCIENCE THESES

This project aims to make a unified database of Czech university
theses from the field of computer science. The theses are often
publicly available at univesity websites, but eah one has a different
search interface, provides different information etc. Hence the
project.

A Python script is made to crawl the websites and gather info
about the theses.

IMPORTANT NOTES:

  - Sometimes some information is unavailable, the crawler can make
    mistakes due to bugs, wrong estimations etc., so don't take the
    info in DB for granted, double check everything.

  - The script make_db.py does not work out of the box and shouldn't
    be just run. It's here more or less for reference and I
    recommend no one uses it.

The database is stored in theses.json file as a JSON array of object
in format:

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

where Person is another JSON object:

{
  name_first:         String, null              person first name
  name_last:          String, null              person last name
  degrees:            [String]                  list of degrees
  sex:                "male", "female", null    estimated sex/gender
}

These faculties have been crawled:

 -- MFF CUNI (Praha)
 -- FIT, FELK, FBMI, FD, FJFI, FSV CTU (Praha)
 -- FIT BUT (Brno)
 -- FI MUNI (Brno)
 -- PEF MENDELU (Brno)
 -- FEI VSB (Ostrava)
 -- FAI UTB (Zlin)
 -- Unicorn College (Praha)

How to work with the DB

In any way you want. However, I provide two tools for easy work:

TODO

Interesting stats gathered from the DB:

TODO




