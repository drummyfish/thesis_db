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
THESIS_DOC = "habilitation"     # Doc.

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
DEGREE_DR = "Dr."
DEGREE_MSC = "MSc"

# just in case:

DEGREE_MUDR = "MUDr."
DEGREE_MDDR = "MDDr."
DEGREE_MVDR = "MVDr."
DEGREE_JUDR = "JUDr."
DEGREE_THDR = "ThDr."

DEGREES_MASTER = [
  DEGREE_ING,
  DEGREE_MGR,
  DEGREE_MSC
  ]

DEGREES_PHD = [
  DEGREE_PHD,
  DEGREE_PHD2
  ]

DEGREES_DR = [
  DEGREE_PHDR,
  DEGREE_RNDR,
  DEGREE_DR,
  DEGREE_MUDR,
  DEGREE_MDDR,
  DEGREE_MVDR,
  DEGREE_JUDR,
  DEGREE_THDR
  ]

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
  DEGREE_MBA,
  DEGREE_DR
  ]

DEGREES_AFTER = [DEGREE_PHD, DEGREE_CSC, DEGREE_MBA] 

GRADE_A = "A"
GRADE_B = "B"
GRADE_C = "C"
GRADE_D = "D"
GRADE_E = "E"
GRADE_F = "F"

ALL_GRADES = [GRADE_A,GRADE_B,GRADE_C,GRADE_D,GRADE_E,GRADE_F]

LANGUAGE_EN = "en"
LANGUAGE_CS = "cs"
LANGUAGE_SK = "sk"

LANGUAGES = [LANGUAGE_CS, LANGUAGE_SK, LANGUAGE_EN]

FACULTY_MFF_CUNI = "MFF CUNI"
FACULTY_FIT_BUT = "FIT BUT"
FACULTY_FI_MUNI = "FI MUNI"
FACULTY_FELK_CTU = "FELK CVUT"
FACULTY_FIT_CTU = "FIT CTU"
FACULTY_FEI_VSB = "FEI VŠB"
FACULTY_FAI_UTB = "FAI UTB"

DEPARTMENT_FIT_BUT_UPGM = "FIT BUT UPGM"     # ustav pocitacove grafiky a multimedii
DEPARTMENT_FIT_BUT_UPSY = "FIT BUT UPSY"     # ustav pocitacovych systemu
DEPARTMENT_FIT_BUT_UIFS = "FIT BUT UIFS"     # ustav informacnich systemu
DEPARTMENT_FIT_BUT_UITS = "FIT BUT UITS"     # ustav inteligentnich systemu

DEPARTMENT_FIT_CTU_KTI = "FIT CTU KTI"       # katedra teoreticke informatiky
DEPARTMENT_FIT_CTU_KSI = "FIT CTU KSI"       # katedra softwaroveho inzenyrstvi
DEPARTMENT_FIT_CTU_KCN = "FIT CTU KCN"       # katedra cislicoveho navrhu
DEPARTMENT_FIT_CTU_KPS = "FIT CTU KPS"       # katedra pocitacovych systemu
DEPARTMENT_FIT_CTU_KAM = "FIT CTU KAM"       # katedra aplikovane matematiky
DEPARTMENT_FELK_CTU_CS = "FELK CTU CS"       # katedra pocitacu
DEPARTMENT_FELK_CTU_DCGI = "FELK CTU DCGI"   # katedra pocitacove grafiky a interakce

DEPARTMENT_FAI_UTB_UAI = "FAI UTB UAI"       # ustav aplikovane informatiky
DEPARTMENT_FAI_UTB_UIUI = "FAI UTB UIUI"     # ustav informatiky a umele inteligence
DEPARTMENT_FAI_UTB_UPKS = "FAI UTB UPKS"     # ustav pocitacovych a komunikacnich systemu
DEPARTMENT_FAI_UTB_UART = "FAI UTB UART"     # ustav automatizace a ridici techniky
DEPARTMENT_FAI_UTB_UELM = "FAI UTB UELM"     # ustav elektroniky a mereni
DEPARTMENT_FAI_UTB_UBI = "FAI UTB UBI"       # ustav bezpecnostniho inzenyrstvi
DEPARTMENT_FAI_UTB_UM = "FAI UTB UM"         # ustav matematiky
DEPARTMENT_FAI_UTB_URP = "FAI UTB URP"       # ustav rizeni procesu

DEPARTMENT_MFF_CUNI_KSI = "MFF CUNI KSI"     # katedra softwaroveho inzenyrstvi
DEPARTMENT_MFF_CUNI_KSVI = "MFF CUNI KSVI"   # katedra softwaru a vyuky informatiky
DEPARTMENT_MFF_CUNI_KAM = "MFF CUNI KAM"     # katedra aplikovane matematiky
DEPARTMENT_MFF_CUNI_D3S = "MFF CUNI D3S"     # katedra distribuovanych a spolehlivych systemu
DEPARTMENT_MFF_CUNI_KTIML = "MFF CUNI KTIML" # katedra teoreticke informatiky a matematicke logiky
DEPARTMENT_MFF_CUNI_SISAL = "MFF CUNI SISAL" # stredisko informaticke site a laboratori
DEPARTMENT_MFF_CUNI_UFAL = "MFF CUNI UFAL"   # ustav formalni a aplikovane lingvistiky
DEPARTMENT_MFF_CUNI_IUUK = "MFF CUNI IUUK"   # informaticky ustav universzity karlovy

FIELD_AI = "artificial intelligence"
FIELD_CG = "computer graphics"
FIELD_NET = "computer networks"
FIELD_HW = "hardware"
FIELD_SP = "speech"
FIELD_SE = "software engineering"
FIELD_SEC = "computer security"
FIELD_TCS = "theoretical computer science"
FIELD_IS = "information systems"
FIELD_BIO = "bioinformatics"
FIELD_ROBO = "robotics"
FIELD_EDU = "education"
FIELD_MAN = "management"
FIELD_OTHER = "other"

ALL_FIELDS = [
  FIELD_AI,
  FIELD_CG,
  FIELD_NET,
  FIELD_HW,
  FIELD_SE,
  FIELD_SEC,
  FIELD_TCS,
  FIELD_TCS,
  FIELD_IS,
  FIELD_BIO,
  FIELD_ROBO,
  FIELD_EDU,
  FIELD_MAN,
  FIELD_OTHER
  ]

KEYWORDS_TO_FIELD = {
  "počítačová grafika": FIELD_CG,
  "computer graphics": FIELD_CG,
  "panorama": FIELD_CG,
  "textures": FIELD_CG,
  "textura": FIELD_CG,
  "ray-tracing": FIELD_CG,
  "ray tracing": FIELD_CG,
  "protocols": FIELD_NET,
  "networking": FIELD_NET,
  "computer networks": FIELD_NET,
  "počítačové sítě": FIELD_NET,
  "CISCO": FIELD_NET,
  "router": FIELD_NET,
  "routers": FIELD_NET,
  "software engineering": FIELD_SE,
  "UML": FIELD_SE,
  "security": FIELD_SEC,
  "computer security": FIELD_SEC,
  "bezpečnost": FIELD_SEC,
  "marketing": FIELD_MAN,
  "management": FIELD_MAN,
  "robotics": FIELD_ROBO,
  "robotika": FIELD_ROBO,
  "hardware": FIELD_HW,
  "CMOS": FIELD_HW,
  "vzdělávání": FIELD_EDU,
  "školství": FIELD_EDU,
  "education": FIELD_EDU,
  "bioinformatika": FIELD_BIO,
  "bioinformatics": FIELD_BIO,
  "artificial intelligence": FIELD_AI,
  "umělá inteligence": FIELD_AI,
  "HTML": FIELD_IS,
  "CSS": FIELD_IS,
  "cryptography": FIELD_SEC,
  "kryptografie": FIELD_SEC,
  "HTTP": FIELD_NET,
  "HTTPS": FIELD_NET,
  "RSA": FIELD_SEC,
  "SSL": FIELD_SEC,
  "hra": FIELD_CG,
  "game": FIELD_CG,
  "procedural generation": FIELD_CG,
  "procedurální generování": FIELD_CG,
  "3D": FIELD_CG,
  "OpenCV": FIELD_CG,
  "segmentace": FIELD_CG,
  "segmentation": FIELD_CG,
  "gen": FIELD_BIO,
  "DNA": FIELD_BIO,
  "síťový tok": FIELD_NET,
  "klient-server": FIELD_NET,
  "client-server": FIELD_NET,
  "RPC": FIELD_NET,
  "database": FIELD_IS,
  "watermark": FIELD_CG,
  "vodoznak": FIELD_CG,
  "HTML5": FIELD_IS,
  "soft body": FIELD_CG,
  "hard body": FIELD_CG,
  "scene graph": FIELD_CG,
  "OpenGL": FIELD_CG,
  "GUI": FIELD_IS,
  "uživatelské rozhraní": FIELD_IS,
  "virtual reality": FIELD_CG,
  "virtuální realita": FIELD_CG,
  "Oculus Rift": FIELD_CG,
  "transistor": FIELD_HW,
  "power": FIELD_HW,
  "výkon": FIELD_HW,
  "ROS": FIELD_ROBO,
  "neural networks": FIELD_AI,
  "compute shaders": FIELD_CG,
  "compute shader": FIELD_CG,
  "photography": FIELD_CG,
  "Node.js": FIELD_IS,
  "PHP": FIELD_IS,
  "voip": FIELD_NET,
  "SQL": FIELD_IS,
  "detekce hran": FIELD_CG,
  "edge detection": FIELD_CG,
  "HDR": FIELD_CG,
  "robot": FIELD_ROBO,
  "SLAM": FIELD_ROBO,
  "zpracování obrazu": FIELD_CG,
  "Direct3D": FIELD_CG,
  "shader": FIELD_CG,
  "shaders": FIELD_CG,
  "GLSL": FIELD_CG,
  "HLSL": FIELD_CG,
  "speech": FIELD_SP,
  "TCP/IP": FIELD_NET,
  "vowels": FIELD_SP,
  "phoneme": FIELD_SP,
  "webová aplikace": FIELD_IS,
  "grammar": FIELD_TCS,
  "grammars": FIELD_TCS,
  "gramatiky": FIELD_TCS,
  "Turing machine": FIELD_TCS,
  "complexity": FIELD_TCS,
  "Turingův stroj": FIELD_TCS,
  "Turingovy stroje": FIELD_TCS,
  "konečné automaty": FIELD_TCS,
  "finite automata": FIELD_TCS,
  "verification": FIELD_TCS,
  "verifikace": FIELD_TCS,
  "DNS": FIELD_NET,
  "IPv4": FIELD_NET,
  "IPv6": FIELD_NET,
  "animation": FIELD_CG,
  "neuronová síť": FIELD_AI,
  "Twitter": FIELD_AI,
  "LPC": FIELD_SP,
  "frontend": FIELD_IS,
  "rendering": FIELD_CG,
  "compiler": FIELD_TCS,
  "překladače": FIELD_TCS,
  "RISC": FIELD_HW,
  "CISC": FIELD_HW,
  "embedded systems": FIELD_HW,
  "rozpoznávání řečníka": FIELD_SP,
  "driver": FIELD_HW,
  "ovladač": FIELD_HW,
  "projektové řízení": FIELD_MAN,
  "P2P": FIELD_NET,
  "clustering": FIELD_AI,
  "shlukování": FIELD_AI,
  "PCA": FIELD_AI,
  "curves": FIELD_CG,
  "strojové učení": FIELD_AI,
  "machine learning": FIELD_AI,
  "bounding box": FIELD_CG,
  "OCR": FIELD_CG,
  "recognition": FIELD_AI,
  "evoluční algoritmy": FIELD_AI,
  "výuka": FIELD_EDU,
  "shadows": FIELD_CG,
  "stíny": FIELD_CG,
  "reflections": FIELD_CG,
  "refractions": FIELD_CG,
  "global illumination": FIELD_CG,
  "convolution": FIELD_CG,
  "vizualizace": FIELD_CG,
  "agent": FIELD_AI,
  "augmented reality": FIELD_CG,
  "voxel": FIELD_CG,
  "klasifikace": FIELD_AI
  }

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
  "Jarmil", "Matěj", "Mikoláš","Branislav","Matej",
  "Dávid", "Samuel"]

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
  "Ingrid", "Ema", "Zlata", "Emílie", "Ivona",
  "Natália", "Viktória"]

def debug_print(print_string):
  print(print_string)

def iterative_load(soup,find_func,process_func):
  result = []

  current = soup.find("body").find_next(find_func)

  while current != None:
    result.append(process_func(current))
    current = current.find_next(find_func)

  return result

def guess_field_from_keywords(keyword_list):
  if keyword_list == None:
    return None

  histogram = {}

  for field in ALL_FIELDS:
    histogram[field] = 0

  for keyword in keyword_list:
    if keyword in KEYWORDS_TO_FIELD:
      histogram[KEYWORDS_TO_FIELD[keyword]] += 1

  best_field = None
  best_score = 0

  for field in histogram:
    if histogram[field] > best_score:
      best_field = field
      best_score = histogram[field]

  return best_field

class Person:
  def __init__(self, from_string=None, first_name_first=True):
   
    self.name_first = None
    self.name_last = None
    self.degrees = []
    self.sex = None

    if from_string != None:
      self.from_string(from_string,first_name_first)

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

    for i in range(len(self.degrees)):
      if self.degrees[i] == DEGREE_PHD2:     # normalize
        self.degrees[i] = DEGREE_PHD

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
    self.author = None
    self.supervisor = None
    self.grade = None
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

  def incorporate_pdf_indo(self, pdf_info):
    self.pages = pdf_info.pages
    self.size = pdf_info.size    
    self.typesetting_system = pdf_info.typesetting_system

    if self.language == None:
      self.language = pdf_info.language

  def normalize(self):              # makes the object consistent
    def print_norm(print_what):
      debug_print("NORMALIZATION: " + print_what)

    if self.opponents == None:
      print_norm("correcting oppoentnts (None to [])")
      self.opponents = []

    if self.keywords == None: 
      print_norm("correcting keywords (None to [])")
      self.keywords = []

    if self.author != None and self.author.name_first == None and self.author.name_first == None:
      print_norm("correcting author (set but empty)")
      self.author = None

    if self.supervisor != None and self.supervisor.name_first == None and self.supervisor.name_first == None:
      print_norm("correcting supervisor (set but empty)")
      self.supervisor = None

    if self.degree != None and not self.degree in DEGREES:
      print_norm("correcting degree (" + str(self.degree) + ")")
      self.degree = None

    if self.language != None and not self.language in LANGUAGES:
      print_norm("correcting language (" + str(self.language) + ")")
      self.language = None 

    if self.grade != None and not self.grade in ALL_GRADES:
      print_norm("correcting grade (" + str(self.grade) + ")")
      self.grade = None

    if self.field != None and not self.field in ALL_FIELDS:
      print_norm("correcting field (" + str(self.field) + ")")
      self.field = None

    if self.degree == DEGREE_PHD2: 
      print_norm("correcting degree: " + DEGREE_PHD2 + " -> " + DEGREE_PHD)
      self.degree = DEGREE_PHD

    if self.grade == GRADE_F and self.defended != False:
      print_norm("F grade but wrong defended value - correcting")
      self.defended = False

    if self.defended == False and self.grade != None and self.grade != GRADE_F:
      print_norm("not defended but wrong grade - correcting")
      self.defended = True
   
    if self.degree == DEGREE_BC and self.kind != THESIS_BACHELOR:
      print_norm("degree Bc. but kind != bachelor - correcting")
      self.kind = THESIS_BACHELOR 

    if self.kind == THESIS_BACHELOR and self.degree != DEGREE_BC:
      print_norm("kind bachelor but degree != Bc. - correcting")
      self.degree = DEGREE_BC

    if self.degree in DEGREES_MASTER and self.kind != THESIS_MASTER:
      print_norm("master degree but kind != master - correcting")
      self.kind = THESIS_MASTER
 
    if self.degree == DEGREE_DOC and self.kind != THESIS_DOC:
      print_norm("doc. degree but kind != doc - correcting")
      self.kind = THESIS_DOC

    if self.kind == THESIS_DOC and self.degree != DEGREE_DOC:
      print_norm("kind doc but degree != doc. - correcting")
      self.degree = DEGREE_DOC

    if self.degree in DEGREES_PHD and self.kind != THESIS_PHD:
      print_norm("PhD degree but kind != phd - correcting")
      self.kind = THESIS_PHD

    if self.kind == THESIS_PHD and self.degree != DEGREE_PHD:
      print_norm("kind phd but degree != PhD - correcting")
      self.degree = DEGREE_PHD

    if self.degree in DEGREES_DR and self.kind != THESIS_DR:
      print_norm("degree dr but kind != dr - correcting")
      self.kind = THESIS_DR

    if self.kind == THESIS_DOC and self.defended != True:
      print_norm("doc thesis and defended != True - correcting")
      self.defended = True

    if self.year != None and not isinstance(self.year,int):
      print_norm("year not int - correcting")
      
      try:
        self.year = int(self.year)

        if self.year < 1000 or self.year > 3000:
          print_norm("wrong year value (" + str(self.year) + ") - clearing")
          self.year = None

      except Exception:
        print_norm("could not convert year to int")

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
      debug_print("could not analyze PDF: " + str(e))

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
    elif thesis_url_substring == "PD":
      result.kind = THESIS_PHD
      result.degree = DEGREE_PHD
    elif url.find("HABIL"):
      result.kind = THESIS_DOC
      result.degree = DEGREE_DOC

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
        result.year = int(text_in_table(u"Disertace:"))
      else: 
        result.year = int(text_in_table(u"Ak.rok:").split("/")[1])
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
 
    try:
      result.keywords = beautify_list(
         soup.find("th",string="Klíčová slova").find_next("td").string.split(",") +
         soup_en.find("th",string="Keywords").find_next("td").string.split(",")
         )
    except Exception as e:
      debug_print("keywords not found:" + str(e)) 

    if result.field == None:
      result.field = guess_field_from_keywords(result.keywords)

    if result.field == None and result.department != None:
      department_to_field = {
        DEPARTMENT_FIT_BUT_UPGM: FIELD_CG,
        DEPARTMENT_FIT_BUT_UPSY: FIELD_HW,
        DEPARTMENT_FIT_BUT_UIFS: FIELD_IS,
        DEPARTMENT_FIT_BUT_UITS: FIELD_AI
        }

      result.field = department_to_field[result.department]
    
    if result.kind == THESIS_DOC:
      result.abstract_cs = text_in_table("Anotace")
      result.abstract_en = text_in_table("Annotation",False)
    else: 
      result.abstract_cs = text_in_table("Abstrakt")
      result.abstract_en = text_in_table("Abstract",False)

    result.url_page = url

    if result.kind == THESIS_DOC:
      result.url_fulltext = FitButDownloader.BASE_URL + soup.find(lambda t: t.name == "a" and t.string != None and t.string[-4:] == ".pdf")["href"][1:]
      result.defended = True
    else:
      result.url_fulltext = FitButDownloader.BASE_URL + soup.find("a",string="Text práce")["href"][1:]
 
      state_string = text_in_table("Stav:")
      
      result.defended = state_string[0] == "o"  # for "pbhájeno"

      if result.defended:
        result.grade = state_string[-1]
      else:
        result.grade = GRADE_F

      if not result.grade in ALL_GRADES:
        result.grade = None    

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

    pdf_info = download_and_analyze_pdf(FitButDownloader.BASE_URL + result.url_fulltext)
 
    result.incorporate_pdf_indo(pdf_info) 

    result.normalize() 
    return result

  def get_thesis_list(self):
    result = []

    for thesis_type in ["BP","DP","PD","DOC"]:
      if thesis_type == "DOC":
        url = FitButDownloader.BASE_URL + "research/habilitace/"
      else:
        url = FitButDownloader.BASE_URL + "study/DP/" + thesis_type + ".php?y=*&ved=&st=&t=&k="

      soup = BeautifulSoup(download_webpage(url),"lxml")

      result += iterative_load(soup,
        lambda t: t.name == "a" and t.contents[0].name == "i",
        lambda t: FitButDownloader.BASE_URL + t["href"][1:]
        )

    return result

#----------------------------------------

class CtuDownloader(FacultyDownloader):

  BASE_URL = "https://dip.felk.cvut.cz/browse/"

  def get_others(self):
    result = []

    url_phd = "https://www.fit.cvut.cz/fakulta/veda/doktorandi/disertacni-prace"
    url_doc = "https://www.fit.cvut.cz/node/2373"

    for other_type in (0,1):
      soup = BeautifulSoup(download_webpage(url_phd if other_type == 0 else url_doc),"lxml")

      current = soup.find("table",class_="tabulka")

      state = 0

      while True:
        current = current.find_next("td")
        
        if current == None:
          break

        if state == 0:    # author
          result.append(Thesis())

          result[-1].defended = True
          result[-1].faculty = FACULTY_FIT_CTU
          result[-1].kind = THESIS_PHD if other_type == 0 else THESIS_DOC
          result[-1].degree = DEGREE_PHD if other_type == 0 else DEGREE_DOC

          result[-1].author = Person()
          result[-1].author.from_string(current.string)
          state += 1
        elif state == 1:  # title and link
          result[-1].title_en = current.contents[1].string
          
          if current.contents[1].name == "a":
            result[-1].url_fulltext = current.contents[1]["href"] 

          result[-1].url_page = url_phd
          state += 1
        elif state == 2:

          if other_type == 0:
            result[-1].year = int(current.contents[1].string.split(".")[2])
          else:
            result[-1].year = int(current.string.split(".")[2])

          state += 1
        elif state == 3:
          state = 0

    return result

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

    def text_in_table(line):
      return soup.find("td",string=line).find_next("td").string

    faculty_string = text_in_table("fakulta")

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
      "K13136": DEPARTMENT_FELK_CTU_CS,
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

    result.department = string_to_department[text_in_table("katedra")]
    result.field = department_to_field[result.department]
 
    result.author = Person()
    result.author.from_string(text_in_table("autor"))

    result.supervisor = Person()
    result.supervisor.from_string(text_in_table("vedoucí"))

    result.year = int(text_in_table("rok"))

    type_string = text_in_table("typ")

    if type_string == "Diplomová práce":
      result.kind = THESIS_MASTER
      result.degree = DEGREE_ING
    elif type_string == "Bakalářská práce":
      result.kind = THESIS_BACHELOR
      result.degree = DEGREE_BC

    result.title_en = text_in_table("název (anglicky)")
    result.title_cs = text_in_table("název")

    result.abstract_en = text_in_table("abstrakt (anglicky)")
    result.abstract_cs = text_in_table("abstrakt")

    result.url_fulltext = CtuDownloader.BASE_URL + soup.find("td",string="fulltext").find_next("a")["href"] 

    pdf_info = download_and_analyze_pdf(result.url_fulltext)
    result.incorporate_pdf_indo(pdf_info)

    result.pages = pdf_info.pages
    result.typesetting_system = pdf_info.typesetting_system
    result.language = pdf_info.language

    result.normalize() 
    return result

#----------------------------------------

class FaiUtbDownloader(FacultyDownloader):

  BASE_URL = "http://digilib.k.utb.cz/"

  def get_thesis_list(self):
    result = []

    lists = (
      (DEPARTMENT_FAI_UTB_UAI,   THESIS_MASTER,    77),
      (DEPARTMENT_FAI_UTB_UART,  THESIS_BACHELOR,  90),
      (DEPARTMENT_FAI_UTB_UIUI,  THESIS_BACHELOR,  94),
      (DEPARTMENT_FAI_UTB_UIUI,  THESIS_MASTER,    154),
      (DEPARTMENT_FAI_UTB_UAI,   THESIS_BACHELOR,  76),
      (DEPARTMENT_FAI_UTB_UART,  THESIS_MASTER,    91),
      (DEPARTMENT_FAI_UTB_UBI,   THESIS_BACHELOR,  92),
      (DEPARTMENT_FAI_UTB_UBI,   THESIS_MASTER,    152),
      (DEPARTMENT_FAI_UTB_UELM,  THESIS_BACHELOR,  93),
      (DEPARTMENT_FAI_UTB_UELM,  THESIS_MASTER,    153),
      (DEPARTMENT_FAI_UTB_UPKS,  THESIS_BACHELOR,  95),
      (DEPARTMENT_FAI_UTB_UPKS,  THESIS_MASTER,    155),
      (DEPARTMENT_FAI_UTB_URP,   THESIS_BACHELOR,  95),
      (DEPARTMENT_FAI_UTB_URP,   THESIS_BACHELOR,  156),
      (0,                        THESIS_PHD,       78)
      )

    for l in lists:
      offset = 0

      while True:    # for each page
        soup = BeautifulSoup(download_webpage("http://digilib.k.utb.cz/handle/10563/" + str(l[2]) + "/recent-submissions?offset=" + str(offset)),"lxml")

        links = iterative_load(soup,
          lambda t: t.name == "a" and t.next_sibling != None and t["href"].find("=") == -1 and t["href"][:3] == "/ha" and t.string != "Next Page",
          lambda t: FaiUtbDownloader.BASE_URL + t["href"][1:],
          )

        result += links

        offset += 20

        if len(links) == 0 or offset > 20000:
          break

    return result

  def get_thesis_info(self, url):
    result = Thesis()
    result.url_page = url
    result.city = CITY_ZLIN

    url += "?show=full"

    result.faculty = FACULTY_FAI_UTB

    soup =  BeautifulSoup(download_webpage(url),"lxml")

    def text_in_table(line):
      tag = soup.find("td",string=line).find_next("td")
      return tag.string if tag.string != None else tag.contents[1].string

    result.year = int(text_in_table("dc.date.issued").split("-")[0])

    result.author = Person()
    result.author.from_string(text_in_table("dc.contributor.author"),False)

    try:
      result.supervisor = Person()
      result.supervisor.from_string(text_in_table("dc.contributor.advisor"),False)
    except Exception as e:
      result.supervisor = None 
      debug_print("supervisor not found: " + str(e))

    result.language = text_in_table("dc.language.iso")
    result.degree = text_in_table("dc.thesis.degree-name")

    if result.degree == DEGREE_BC:
      result.kind = THESIS_BACHELOR
    elif result.degree in DEGREES_MASTER:
      result.kind = THESIS_MASTER
    elif result.degree in DEGREES_PHD:
      result.kind = THESIS_PHD

    try:
      if result.kind != THESIS_PHD:
        result.grade = text_in_table("utb.result.grade")
    except Exception as e:
      debug_print("grade not found: " + str(e))

    if result.grade in (GRADE_A, GRADE_B, GRADE_C, GRADE_D, GRADE_E):
      result.defended = True
    elif result.grade == GRADE_F:
      result.defended = False

    result.title_cs = text_in_table("dc.title")
    result.title_en = text_in_table("dc.title.alternative")

    if result.title_cs == result.title_en:
      result.title_cs = None

    result.abstract_cs = text_in_table("dc.description.abstract")
    result.abstract_en = text_in_table("dc.description.abstract-translated")

    result.opponents = iterative_load(soup,
      lambda t: t.name == "td" and t.string == "dc.contributor.referee",
      lambda t: Person(t.find_next("td").string,False)
      )
   
    result.keywords = iterative_load(soup,
      lambda t: t.name == "td" and t.string == "dc.subject",
      lambda t: t.find_next("td").contents[1].string)

    grantor_string = text_in_table("dc.thesis.degree-grantor")
 
    if grantor_string.find("aplikované in") >= 0:
      result.department = DEPARTMENT_FAI_UTB_UAI
    elif grantor_string.find("automatizace a") >= 0:
      result.department = DEPARTMENT_FAI_UTB_UART
    elif grantor_string.find("bezpečnostního in") >= 0:
      result.department = DEPARTMENT_FAI_UTB_UBI
      result.field = FIELD_SEC
    elif grantor_string.find("elektrotechniky a") >= 0:
      result.department = DEPARTMENT_FAI_UTB_UELM
    elif grantor_string.find("umělé in") >= 0:
      result.department = DEPARTMENT_FAI_UTB_UIUI
    elif grantor_string.find("počítačových a kom") >= 0:
      result.department = DEPARTMENT_FAI_UTB_UPKS
    elif grantor_string.find("řízení proc") >= 0:
      result.department = DEPARTMENT_FAI_UTB_URP

    if result.field == None:
      result.field = guess_field_from_keywords(result.keywords)
    
    result.url_fulltext = FaiUtbDownloader.BASE_URL + soup.find("table",class_="ds-table file-list").find_next("a")["href"] 

    if result.url_fulltext.find(".pdf") >= 0:
      pdf_info = download_and_analyze_pdf(result.url_fulltext)
      result.incorporate_pdf_indo(pdf_info)

    result.normalize() 
    return result

#---------------------------------------

class MffCuniDownloader(FacultyDownloader):

  def get_thesis_info(self, url):
    result = Thesis()

    result.city = CITY_PRAHA
    result.faculty = FACULTY_MFF_CUNI
    result.url_page = url

    soup = BeautifulSoup(download_webpage(url),"lxml")

    def text_in_table(line):
      return soup.find(lambda t: t.name == "div" and t.string != None and t.string.lstrip().rstrip() == line).find_next("span").string.lstrip().rstrip()

    type_string = text_in_table("Program studia:")

    if not starts_with(type_string,"Informatika"):
      return None

    lang_string = text_in_table("Jazyk práce:")

    if lang_string == "Čeština":
      result.language = LANGUAGE_CS
    if lang_string == "Angličtina":
      result.language = LANGUAGE_EN
    if lang_string == "Slovenština":
      result.language = LANGUAGE_SK

    try:
      if result.language in (LANGUAGE_CS,LANGUAGE_SK): 
        result.title_cs = text_in_table("Název:")
        result.title_en = text_in_table("Název v angličtině:")
      if result.language == LANGUAGE_EN:
        try: 
          result.title_en = text_in_table("Název:")
          result.title_cs = text_in_table("Název v češtině:")
        except Exception:
          result.title_en = text_in_table("Název v angličtině:")
          result.title_cs = text_in_table("Název v češtině:")
    except Exception as e:
      debug_print("could not resolve title: " + str(e))

    if result.language == LANGUAGE_EN and result.title_cs != None and result.title_en == None:
      result.title_en = result.title_cs
      result.title_cs = None

    result.year = int(text_in_table("Datum obhajoby:").split(".")[-1])

    try:
      result.abstract_cs = text_in_table("Abstrakt:")   
      result.abstract_en = text_in_table("Abstract v angličtině:")   
    except Exception as e:
      debug_print("could not resolve abstract: " + str(e))

    try:
      result.author = Person()
      result.author.from_string(text_in_table("Autor:"))
    except Exception as e:
      debug_print("could not resolve author: " + str(e))

    try:
      result.supervisor = Person()
      result.supervisor.from_string(text_in_table("Vedoucí:"))
    except Exception as e:
      debug_print("could not resolve supervisor: " + str(e))

    result.degree = text_in_table("Přidělovaný titul:")

    if result.degree == DEGREE_BC:
      result.kind = THESIS_BACHELOR
    elif result.degree in DEGREES_MASTER:
      result.kind = THESIS_MASTER
    elif result.degree in DEGREES_PHD:
      result.kind = THESIS_PHD
    elif result.degree in DEGREES_DR:
      result.kind = THESIS_DR
    elif result.degree == DEGREE_DOC:
      result.kind = THESIS_DOC

    try:
      result.opponents = [Person()]
      result.opponents[0].from_string(text_in_table("Oponent:"))
    except Exception as e:
      result.opponents = []
      debug_print("could not resolve opponent: " + str(e)) 

    string_to_grade = {
        u"výborně": GRADE_A,
        u"velmi dobře": GRADE_B,
        u"dobře": GRADE_C,
        u"uspokojivě": GRADE_D,
        u"prospěl/a": GRADE_E,
        u"neprospěl/a": GRADE_F
      }

    try:
      result.keywords = []

      for s in ("Klíčová slova:","Klíčová slova v angličtině:","Klíčová slova v češtině:"):
        try:
          result.keywords += text_in_table(s).split(";")
        except Exception:
          pass
    except Exception as e:
      debug_print("could not keywords: " + str(e)) 

    if len(result.keywords) == 0:
      result.keywords = None
    else:
      result.keywords = beautify_list(result.keywords) 
      result.field = guess_field_from_keywords(result.keywords)

    if result.kind in (THESIS_BACHELOR, THESIS_MASTER):
      result.grade = string_to_grade[text_in_table("Výsledek obhajoby:")]
      result.defended = result.grade != GRADE_F
    elif result.kind == THESIS_PHD:
      result.defended = text_in_table("Výsledek obhajoby:")[0] == "p"
    elif result.kind == THESIS_DR:
      result.defended = text_in_table("Výsledek obhajoby:")[0] == "u"

    result.url_fulltext = soup.find("a",class_="btn")["href"]

    pdf_info = download_and_analyze_pdf(result.url_fulltext)
    result.incorporate_pdf_indo(pdf_info)

    department_string = text_in_table("Pracoviště:")

    if department_string.find("KSVI") >= 0:
      result.department = DEPARTMENT_MFF_CUNI_KSVI
    elif department_string.find("KSI") >= 0:
      result.department = DEPARTMENT_MFF_CUNI_KSI
    elif department_string.find("KAM") >= 0:
      result.department = DEPARTMENT_MFF_CUNI_KAM
    elif department_string.find("D3S") >= 0:
      result.department = DEPARTMENT_MFF_CUNI_D3S
    elif department_string.find("KTIML") >= 0:
      result.department = DEPARTMENT_MFF_CUNI_KTIML
      result.field = FIELD_TCS
    elif department_string.find("SISAL") >= 0:
      result.department = DEPARTMENT_MFF_CUNI_SISAL
    elif department_string.find("UFAL") >= 0:
      result.department = DEPARTMENT_MFF_CUNI_UFAL
      result.field = FIELD_SP
    elif department_string.find("IUUK") >= 0:
      result.department = DEPARTMENT_MFF_CUNI_IUUK
    
    result.normalize() 
    return result    

  def get_thesis_list(self):
    result = []

    page = 1

    while True:      # for each page
      soup = BeautifulSoup(download_webpage("https://is.cuni.cz/webapps/zzp/search/?______searchform___search=&______facetform___facets___faculty%5B%5D=11320&tab_searchas=basic&lang=cs&PSzzpSearchListbasic=10&SOzzpSearchListbasic=&_sessionId=0&______searchform___butsearch=Vyhledat&PNzzpSearchListbasic=" + str(page)),"lxml")

      current = soup.find("span",class_="title")

      links = iterative_load(soup,
        lambda t: t.name == "div" and t.get("class") != None and t.get("class")[0] == "zzp-work-maintitle",
        lambda t: t.contents[1]["href"]
        )

      result += links

      page += 1

      break

      if len(links) == 0 or page > 1000:
        break

    return result

#----------------------------------------

class FeiVsbDownloader(FacultyDownloader):
  BASE_URL = "http://dspace.vsb.cz/"

  def get_thesis_list(self):
    result = []
    records = 500
    offset = 0

    while True:    # for each page
      soup = BeautifulSoup(download_webpage(FeiVsbDownloader.BASE_URL + "handle/10084/2564/browse?order=ASC&rpp=" + str(records) + "&sort_by=2&etal=-1&offset=" + str(offset) + "&type=dateissued"),"lxml")
      current = soup.find("h2")

      links = iterative_load(soup,
        lambda t: t.name == "h4",
        lambda t: FeiVsbDownloader.BASE_URL + t.find_next("a")["href"]
        )

      result += links

      offset += records

      if len(links) == 0 or offset > 20000:
        break

    return result

  def get_thesis_info(self, url):
    url = url + "?show=full"
    result = Thesis()

    result.url_page = url

    result.faculty = FACULTY_FEI_VSB
    result.city = CITY_OSTRAVA

    soup =  BeautifulSoup(download_webpage(url),"lxml")

    def text_in_table(line):
      return soup.find("td",string=line).find_next("td").string

    type_string = text_in_table("dc.type")

    if starts_with(type_string,"Diplom"):
      result.kind = THESIS_MASTER
    elif starts_with(type_string,"Baka"):
      result.kind = THESIS_BACHELOR
      result.degree = DEGREE_BC
    elif starts_with(type_string,"Diser"):
      result.kind = THESIS_PHD
      result.degree = DEGREE_PHD
    elif starts_with(type_string,"Habil"):
      result.kind = THESIS_DOC
      result.degree = DEGREE_DOC

    result.author = Person()
    result.author.from_string(text_in_table("dc.contributor.author"),False)

    result.supervisor = Person()
    result.supervisor.from_string(text_in_table("dc.contributor.advisor"),False)

    result.year = int(text_in_table("dc.date.issued"))
    result.language = text_in_table("dc.language.iso")

    if result.language in [LANGUAGE_CS,LANGUAGE_SK]:
      try:
        result.title_cs = text_in_table("dc.title")
        result.title_en = text_in_table("dc.title.alternative")
      except Exception as e:
        pass
    else:
      try:
        result.title_en = text_in_table("dc.title")
        result.title_cs = text_in_table("dc.title.alternative")
      except Exception as e:
        pass

    try:
      abstract_tag = soup.find("td",string="dc.description.abstract")
      result.abstract_cs = abstract_tag.find_next("td").string
      abstract_tag = abstract_tag.find_next("td",string="dc.description.abstract")
      result.abstract_en = abstract_tag.find_next("td").string
    except Exception as e:
      debug_print("could not resolve abstract: " + str(e))

    result.keywords = iterative_load(
      soup,
      lambda t: t.name == "td" and t.string == "dc.subject",
      lambda t: t.find_next("td").string)

    result.field = guess_field_from_keywords(result.keywords)

    result.pages = text_in_table("dc.format").split(" ")[0]

    result.normalize() 
    return result

#----------------------------------------

class FiMuniDownloader(FacultyDownloader):

  BASE_URL = "https://is.muni.cz/"

  def get_thesis_list(self):
    result = []

    soup = BeautifulSoup(download_webpage("https://is.muni.cz/thesis/?FAK=1433;PRI=-;ROK=-;TIT=-;PRA=-;vypsat=1;exppar=1;por=1"),"lxml")

    page_links = iterative_load(soup,
      lambda t: t.name == "nobr" and t.parent.name == "font",
      lambda t: FiMuniDownloader.BASE_URL + "thesis" + t.find_next("a")["href"][1:])

    for page in page_links:   # first page already loaded
      soup = BeautifulSoup(download_webpage(page),"lxml")

      result += iterative_load(soup,
        lambda t: t.name == "a" and t.string == "archiv",
        lambda t: FiMuniDownloader.BASE_URL[:-1] + t["href"])

    return result 

#----------------------------------------

fit_vut = FitButDownloader()
ctu = CtuDownloader()
fai_utb = FaiUtbDownloader()
mff_cuni = MffCuniDownloader()
fei_vsb = FeiVsbDownloader()
fi_muni = FiMuniDownloader()

#print(fit_vut.get_thesis_info("http://www.fit.vutbr.cz/study/DP/BP.php?id=16335&y=0&st=%E8%ED%BE"))
#print(fei_vsb.get_thesis_info("http://dspace.vsb.cz/handle/10084/116764"))
#print(ctu.get_thesis_info("https://dip.felk.cvut.cz/browse/details.php?f=F8&d=K103&y=2014&a=pichldom&t=bach"))
#print(fai_utb.get_thesis_info("http://digilib.k.utb.cz/handle/10563/38911"))

for l in fi_muni.get_thesis_list():
  print(l)
