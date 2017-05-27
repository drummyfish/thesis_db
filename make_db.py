#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
import ssl
import langdetect
import json
from PyPDF2 import PdfFileReader
from bs4 import BeautifulSoup
import os
import sys

reload(sys)
sys.setdefaultencoding("utf8")

ANALYZE_PDFS = False

THESIS_BACHELOR = "bachelor"    # Bc.
THESIS_MASTER = "master"        # Ing., Mgr., ...
THESIS_PHD = "PhD"              # PhD.
THESIS_DR = "small doctorate"   # PhDr, RNDr, ...

DEGREE_BC = "Bc."
DEGREE_ING = "Ing."
DEGREE_MGR = "Mgr."
DEGREE_PHD = "PhD."
DEGREE_PHD2 = "Ph.D."
DEGREE_PHDR = "PhDr."
DEGREE_RNDR = "RNDr."
DEGREE_PROF = "prof."
DEGREE_DOC = "doc."
DEGREE_CSC = "CSc."
DEGREE_MBA = "MBA"

DEGREES = [
  DEGREE_BC,
  DEGREE_ING,
  DEGREE_MGR,
  DEGREE_PHD,
  DEGREE_PHD2,
  DEGREE_PHDR,
  DEGREE_RNDR,
  DEGREE_PROF,
  DEGREE_DOC,
  DEGREE_CSC,
  DEGREE_MBA
  ]

DEGREES_AFTER = [DEGREE_PHD, DEGREE_CSC, DEGREE_MBA] 

MARK_A = "A"
MARK_B = "B"
MARK_C = "C"
MARK_D = "D"
MARK_E = "E"
MARK_F = "F"

ALL_MARKS = [MARK_A,MARK_B,MARK_C,MARK_D,MARK_E,MARK_F]

LANGUAGE_EN = "en"
LANGUAGE_CS = "cs"
LANGUAGE_SK = "sk"

FACULTY_MFF_CUNI = "MFF CUNI"
FACULTY_FIT_BUT = "FIT BUT"
FACULTY_FI_MUNI = "FI MUNI"
FACULTY_FELK_CTU = "FELK CVUT"
FACULTY_FIT_CTU = "FIT CTU"
FACULTY_FEI_VSB = "FEI VŠB"
FACULTY_FAI_UTB = "FAI UTB"

DEPARTMENT_FIT_BUT_UPGM = "UPGM"   # ustav pocitacove grafiky a multimedii
DEPARTMENT_FIT_BUT_UPSY = "UPSY"   # ustav pocitacovych systemu
DEPARTMENT_FIT_BUT_UIFS = "UIFS"   # ustav informacnich systemu
DEPARTMENT_FIT_BUT_UITS = "UITS"   # ustav inteligentnich systemu

DEPARTMENT_FIT_CTU_KTI = "KTI"     # katedra teoreticke informatiky
DEPARTMENT_FIT_CTU_KSI = "KSI"     # katedra softwaroveho inzenyrstvi
DEPARTMENT_FIT_CTU_KCN = "KCN"     # katedra cislicoveho navrhu
DEPARTMENT_FIT_CTU_KPS = "KPS"     # katedra pocitacovych systemu
DEPARTMENT_FIT_CTU_KAM = "KAM"     # katedra aplikovane matematiky
DEPARTMENT_FELK_CTU_CS = "CS"      # katedra pocitacu
DEPARTMENT_FELK_CTU_DCGI = "DCGI"  # katedra pocitacove grafiky a interakce

FIELD_AI = "artificial intelligence"
FIELD_CG = "computer graphics"
FIELD_NET = "computer networks"
FIELD_HW = "hardware"
FIELD_SE = "software engineering"
FIELD_SEC = "computer security"
FIELD_TCS = "theoretical computer science"
FIELD_IS = "information systems"
FIELD_BIO = "bioinformatics"
FIELD_ROBO = "robotics"
FIELD_EDU = "education"
FIELD_MAN = "management"
FIELD_OTHER = "other"

CITY_PRAHA = "Praha"
CITY_BRNO = "Brno"
CITY_OSTRAVA = "Ostrava"
CITY_ZLIN = "Zlín"

SYSTEM_LATEX = "LaTeX"
SYSTEM_WORD = "MS Word"
SYSTEM_OPEN_OFFICE = "Open Office"
SYSTEM_TYPEWRITER = "typewriter"
SYSTEM_OTHER = "other"

NAMES_MALE = ["Jiří", "Jan", "Petr", "Pavel", "Jaroslav",
  "Martin", "Tomáš", "Miroslav", "Miloslav", "František",
  "Josef", "Štěpán", "Václav", "Michal", "Karel", "Milan",
  "Vladimír", "David", "Jakub", "Lukáš", "Ladislav",
  "Stanislav", "Roman", "Ondřej", "Radek", "Marek",
  "Daniel", "Vojtěch", "Filip", "Jaromír", "Ivan",
  "Aleš", "Oldřich", "Libor", "Rudolf", "Jindřich",
  "Miloš", "Adam", "Lubomír", "Patrik", "Dominik",
  "Bohumil", "Luboš", "Robert", "Radim", "Richard",
  "Ivo", "Luděk", "Bohuslav", "Alois", "Vladislav",
  "Dušan", "Vít", "Kamil", "Jozef", "Zbyněk", "Štefan",
  "Viktor", "Michael", "Emil", "Eduard", "Vítězslav",
  "Ludvík", "René", "Marcel", "Dalibor", "Otakar",
  "Radomír", "Bedřich", "Radek", "Šimon", "Radovan",
  "Leoš", "Přemysl", "Igor", "Alexandr", "Otto",
  "Arnošt", "Kryštof", "Adolf", "Svatopluk", "Lumír",
  "Erik", "Evžen", "Alexander", "Robin", "Vlastislav",
  "Čestmír", "Juraj", "Tadeáš", "Mojmír", "Radoslav",
  "Marián", "Andrej", "Tibor", "Mikuláš", "Oto",
  "Dan", "Daniel", "Emanuel", "Čeněk", "Hynek",
  "Jarmil", "Matěj", "Mikoláš"]

NAMES_FEMALE = ["Marie", "Jana", "Eva", "Anna", "Hana",
  "Věra", "Lenka", "Alena", "Jaroslava", "Lucie",
  "Petra", "Kateřina", "Helena", "Ludmila", "Jitka",
  "Jarmila", "Veronika", "Martina", "Jiřina", "Michaela",
  "Tereza", "Vlasta", "Monika", "Zuzana", "Markéta",
  "Marcela", "Dagmar", "Božena", "Libuše", "Dana",
  "Růžena", "Marta", "Barbora", "Miroslava", "Eliška",
  "Irena", "Kristýna", "Pavla", "Olga", "Milada",
  "Andrea", "Iveta", "Pavlína", "Šárka", "Zdenka",
  "Blanka", "Nikola", "Renata", "Gabriela",
  "Klára", "Gabriela", "Simona", "Radka", "Iva",
  "Denisa", "Daniela", "Květoslava", "Romana",
  "Stanislava", "Natálie", "Ilona", "Aneta",
  "Anežka", "Soňa", "Kamila", "Drahomíra",
  "Františka", "Alžběta", "Vendula", "Bohumila",
  "Julie", "Štěpánka", "Alice", "Žaneta", "Hedvika",
  "Silvie", "Alexandra", "Edita", "Leona", "Dita",
  "Sabina", "Lada", "Radmila", "Taťána", "Darina",
  "Linda", "Ivana", "Michala", "Karolína", "Sára",
  "Ingrid", "Ema", "Zlata", "Emílie", "Ivona"]

def debug_print(print_string):
  print(print_string)

class Person:
  def __init__(self):
   
    self.name_first = None
    self.name_last = None
    self.degrees = []
    self.sex = None

  def __str__(self):
    result = ""

    for degree in self.degrees:
      result += degree + " "

    if self.name_first != None and self.name_last != None:
      result += self.name_first + " " + self.name_last

    return result

  def from_string(self, input_string, first_name_first=True):
    parts = input_string.replace(",","").split()

    self.degrees = [item for item in parts if item in DEGREES]
 
    parts = filter(lambda item: item not in DEGREES,parts)

    self.name_first = parts[0 if first_name_first else 1]
    self.name_last = parts[1 if first_name_first else 0]

    self.estimate_sex()

  def estimate_sex(self):
    if self.name_first != None:
      if self.name_first in NAMES_MALE:
        self.sex = "male"
      elif self.name_first in NAMES_FEMALE:
        self.sex = "female" 

    if self.sex == None and self.name_last != None and self.name_last[-1] == "á":
      self.sex = "female"

class Thesis():
  def __init__(self):

    self.title_en = None
    self.title_cs = None
    self.language = None
    self.keywords = []
    self.year = None
    self.city = None
    self.kind = None
    self.degree = None
    self.faculty = None
    self.department = None
    self.url_page = None
    self.url_fulltext = None
    self.author = Person()
    self.supervisor = Person()
    self.mark = None
    self.defended = None
    self.pages = None
    self.typesetting_system = None
    self.opponents = []
    self.field = None
    self.abstract_en = None
    self.abstract_cs = None
    self.size = None                # in bytes

  def __str__(self):
    return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4, ensure_ascii=False)

class PDFInfo:
  def __init__(self, filename):
    self.language = None
    self.pages = None
    self.typesetting_system = None
    self.size = None                     # in bytes
    self.characters = None

    if not ANALYZE_PDFS:
      return

    try:
      input_pdf = PdfFileReader(open(filename,"rb"))

      self.pages = input_pdf.getNumPages()
     
      self.pdf_text = ""

      for page in range(self.pages):
        self.pdf_text += input_pdf.getPage(page).extractText()

      self.characters = len(self.pdf_text)

      self.language = langdetect.detect(self.pdf_text)    # we suppose page 10 exists and has some text
 
      created_with = input_pdf.getDocumentInfo().creator

      if created_with[:5].lower() == "latex":
        self.typesetting_system = SYSTEM_LATEX
      elif created_with.lower().find("word"):
        self.typesetting_system = SYSTEM_WORD
      else:
        self.typesetting_system = None

      self.size = os.path.getsize(filename)

    except Exception as e:
      debug_print("ERROR: could not analyze PDF: " + str(e))

def beautify_list(keywords):  # removes duplicates, empties, strips etc.
  return [item.decode("utf-8") for item in map(lambda s: s.lstrip().rstrip(), list(set(keywords))) if len(item) > 1]

def download_webpage(url):
  gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
  return urllib2.urlopen(url,context=gcontext).read()

def download_to_file(url, filename):
  gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
  web_file = urllib2.urlopen(url,context=gcontext)

  with open(filename, "wb") as local_file:
    local_file.write(web_file.read()) 

def download_and_analyze_pdf(url):
  if not ANALYZE_PDFS:
    return PDFInfo(None) 

  download_to_file(url,"tmp.pdf")
  return PDFInfo("tmp.pdf")

def get_file_text(filename):
  with open(filename, "r") as input_file:
    return input_file.read()

def starts_with(what, prefix):
  return what[:len(prefix.decode("utf-8"))] == prefix

class FacultyDownloader:              # base class for downloaders of theses of a single faculty
  def get_thesis_list(self):          # get list of links to these pages
    return []

  def get_thesis_info(self,url):
    return Thesis()

  def get_theses(self):
    result = []
    these_list = self.get_thesis_list()
    
    for thesis_url in these_list:
      result.append(self.get_thesis_info(thesis_url))

    return result

#----------------------------------------

class FitButDownloader(FacultyDownloader):

  BASE_URL = "http://www.fit.vutbr.cz/"

  def get_thesis_info(self, url): 
    result = Thesis()

    result.faculty = FACULTY_FIT_BUT
    result.city = CITY_BRNO

    index = url.find("/DP/") + 4 
    thesis_url_substring = url[index:index + 2]
    
    if thesis_url_substring == "BP":
      result.kind = THESIS_BACHELOR
      result.degree = DEGREE_BC
    elif thesis_url_substring == "DP":
      result.kind = THESIS_MASTER
      result.degree = DEGREE_ING
    else:
      result.kind = THESIS_PHD
      result.degree = DEGREE_PHD

    url = url.replace(".php.cs",".php").replace(".php.en",".php") 
    soup = BeautifulSoup(download_webpage(url.replace(".php",".php.cs",1)),"lxml")
    soup_en = BeautifulSoup(download_webpage(url.replace(".php",".php.en",1)),"lxml")

    def text_in_table(line, cs=True):
      if cs:
        return soup.find("th",string=line).find_next("td").string
      else:
        return soup_en.find("th",string=line).find_next("td").string

    def person_from_table(line):
      try:
        new_person = Person()
        new_person.from_string(text_in_table(line),False)
        return new_person
      except Exception as e:
        debug_print(line + " not found: " + str(e))
        return None

    result.author = person_from_table(u"Student:")
    result.supervisor = person_from_table(u"Vedoucí:")

    if result.kind != THESIS_PHD:
      result.opponents = [person_from_table(u"Oponent:")]

    try:
      if result.kind == THESIS_PHD:
        result.year = text_in_table(u"Disertace:")
      else: 
        result.year = text_in_table(u"Ak.rok:").split("/")[1]
    except Exception as e:
      debug_print("year not found: " + str(e))

    result.title_en = soup_en.find("h2").string
    result.title_cs = soup.find("h2").string

    try:
      branch_string = text_in_table(u"Obor studia:")

      prefix_fiels = (
        (u"Bezpečnost",             FIELD_SEC),
        (u"Počítačová grafika",     FIELD_CG),
        (u"Informační systémy",     FIELD_IS),
        (u"Počítačové a vestavěné", FIELD_HW),
        (u"Inteligentní",           FIELD_AI),
        (u"Počítačové sítě",        FIELD_NET),
        (u"Bioinformatika",         FIELD_BIO),
        ("Management",             FIELD_MAN)
        )

      for item in prefix_fiels:
        if starts_with(branch_string,item[0]):
          result.field = item[1]
          break

    except Exception as e:
      debug_print("branch could not be resolved: " + str(e))

    try:
      department_string = text_in_table("Ústav:")

      prefix_departments = (
        (u"Ústav inteligentních",     DEPARTMENT_FIT_BUT_UITS),
        (u"Ústav počítačové",         DEPARTMENT_FIT_BUT_UPGM),
        (u"Ústav informačních",       DEPARTMENT_FIT_BUT_UIFS),
        (u"Ústav počítačových",       DEPARTMENT_FIT_BUT_UPSY)
        )
 
      for item in prefix_departments:
        if starts_with(department_string,item[0]):
          result.department = item[1]
          break

    except Exception as e:
      debug_print("department could not be resolved: " + str(e))

    if result.field == None and result.department != None:
      department_to_field = {
        DEPARTMENT_FIT_BUT_UPGM: FIELD_CG,
        DEPARTMENT_FIT_BUT_UPSY: FIELD_HW,
        DEPARTMENT_FIT_BUT_UIFS: FIELD_IS,
        DEPARTMENT_FIT_BUT_UITS: FIELD_AI
        }

      result.field = department_to_field[result.department]
     
    result.abstract_cs = text_in_table("Abstrakt")
    result.abstract_en = text_in_table("Abstract",False)

    result.url_page = url

    result.url_fulltext = FitButDownloader.BASE_URL + soup.find("a",string="Text práce")["href"][1:]

    state_string = text_in_table("Stav:") 

    result.defended = state_string[0] == "o"  # for "pbhájeno"

    if result.defended:
      result.mark = state_string[-1]
    else:
      result.mark = MARK_F

    if not result.mark in ALL_MARKS:
      result.mark = None    

    try:
      lang_string = text_in_table("Jazyk:")

      if lang_string == "čeština":
        result.language = LANGUAGE_CS
      elif lang_string == "angličtina":
        result.language = LANGUAGE_EN
      elif lang_string == "slovenština":
        result.language = LANGUAGE_SK
    except Exception as e:
      debug_print("language not found: " + str(e))

    try:
      result.keywords = beautify_list(
         soup.find("th",string="Klíčová slova").find_next("td").string.split(",") +
         soup_en.find("th",string="Keywords").find_next("td").string.split(",")
         )
    except Exception as e:
      debug_print("keywords not found:" + str(e)) 

    pdf_info = download_and_analyze_pdf(FitButDownloader.BASE_URL + result.url_fulltext)
  
    result.pages = pdf_info.pages

    if result.language == None:
      result.language = pdf_info.language

    result.typesetting_system = pdf_info.typesetting_system   
    result.size = pdf_info.size
 
    return result

  def get_thesis_list(self):
    def is_thesis_link(tag):
      return tag.name == "a" and tag.contents[0].name == "i"

    result = []

    for thesis_type in ["BP","DP","PD"]:
      soup = BeautifulSoup(download_webpage(FitButDownloader.BASE_URL + "study/DP/" + thesis_type + ".php?y=*&ved=&st=&t=&k="),"lxml")

      link_tags = soup.find_all(is_thesis_link)

      for link_tag in link_tags:
        result.append(link_tag["href"])
    
    return result

#----------------------------------------

class CtuDownloader(FacultyDownloader):

  BASE_URL = "https://dip.felk.cvut.cz/browse/"

  def get_thesis_info(self, url): 
    pass

  def get_thesis_list(self):
    result = []

    for faculty in ("F8","F3"):
      departments = range(101,106) if faculty == "F8" else (13136,13139)

      for department in departments:
        url = CtuDownloader.BASE_URL + "department.php?f=" + faculty + "&d=K" + str(department)

        page_soup = BeautifulSoup(download_webpage(url),"lxml")

        year_urls =  page_soup.find_all("a")[:-1]

        year_urls = map(lambda item: CtuDownloader.BASE_URL + item["href"],year_urls)

        for year_url in year_urls:
          page_soup2 = BeautifulSoup(download_webpage(year_url),"lxml")
          result = result + map(lambda item: CtuDownloader.BASE_URL + item["href"],page_soup2.find_all("a")[:-1])

    return result    

  def get_thesis_info(self, url):
    result = Thesis()

    soup = BeautifulSoup(download_webpage(url),"lxml")
 
    result.url_page = url
    result.city = CITY_PRAHA 

    def get_table_text(line):
      return soup.find("td",string=line).find_next("td").string

    faculty_string = get_table_text("fakulta")

    if faculty_string == "F3":
      result.faculty = FACULTY_FELK_CTU
    else:
      result.faculty = FACULTY_FIT_CTU

    string_to_department = {
      "K101": DEPARTMENT_FIT_CTU_KTI,
      "K102": DEPARTMENT_FIT_CTU_KSI,
      "K103": DEPARTMENT_FIT_CTU_KCN,
      "K104": DEPARTMENT_FIT_CTU_KPS,
      "K105": DEPARTMENT_FIT_CTU_KAM,
      "K13131": DEPARTMENT_FELK_CTU_CS,
      "K13139": DEPARTMENT_FELK_CTU_DCGI 
      }

    department_to_field = {
      DEPARTMENT_FIT_CTU_KTI: FIELD_TCS,
      DEPARTMENT_FIT_CTU_KSI: FIELD_SE,
      DEPARTMENT_FIT_CTU_KCN: FIELD_HW,
      DEPARTMENT_FIT_CTU_KPS: FIELD_HW,
      DEPARTMENT_FIT_CTU_KAM: FIELD_TCS,
      DEPARTMENT_FELK_CTU_CS: FIELD_HW,
      DEPARTMENT_FELK_CTU_DCGI: FIELD_CG
      }

    result.department = string_to_department[get_table_text("katedra")]
    result.field = department_to_field[result.department]
 
    result.author = Person()
    result.author.from_string(get_table_text("autor"))

    result.supervisor = Person()
    result.supervisor.from_string(get_table_text("vedoucí"))

    result.year = get_table_text("rok")

    type_string = get_table_text("typ")

    if type_string == "Diplomová práce":
      result.kind = THESIS_MASTER
      result.degree = DEGREE_ING
    elif type_string == "Bakalářská práce":
      result.kind = THESIS_BACHELOR
      result.degree = DEGREE_BC

    result.title_en = get_table_text("název (anglicky)")
    result.title_cs = get_table_text("název")

    result.abstract_en = get_table_text("abstrakt (anglicky)")
    result.abstract_cs = get_table_text("abstrakt")

    result.url_fulltext = CtuDownloader.BASE_URL + soup.find("td",string="fulltext").find_next("a")["href"] 

    pdf_info = download_and_analyze_pdf(result.url_fulltext)

    result.pages = pdf_info.pages
    result.typesetting_system = pdf_info.typesetting_system
    result.language = pdf_info.language

    return result

#----------------------------------------

#f = FitButDownloader()
#info = f.get_thesis_info("http://www.fit.vutbr.cz/study/DP/BP.php?id=2581&y=0")
#print(str(info))

f2 = CtuDownloader()

#l = f2.get_thesis_list()
#for ll in l:
#  print(ll)

print(f2.get_thesis_info("https://dip.felk.cvut.cz/browse/details.php?f=F3&d=K13139&y=1988&a=pytelma1&t=bach"))


