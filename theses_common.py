#!/usr/bin/env python
# -*- coding: utf-8 -*-

# import standard libs:
import urllib
import urllib2
import ssl
import json
import random
import os
import sys
import traceback
import copy

# import non-standard libs:

def import_warning_print(module_name):
  print("Warning: could not load module " + module_name)

try:
  import langdetect
except Exception:
  import_warning_print("langdetect")

try:
  from PyPDF2 import PdfFileReader
except Exception:
  import_warning_print("PyPDF2")

try:
  from bs4 import BeautifulSoup
  from bs4 import element
except Exception:
  import_warning_print("BeautifulSoup")

try:
  import requests
except Exception:
  import_warning_print("requests")

THESIS_BACHELOR = "bachelor"    # Bc.
THESIS_MASTER = "master"        # Ing., Mgr., ...
THESIS_PHD = "PhD"              # PhD.
THESIS_DR = "small doctorate"   # PhDr, RNDr, ...
THESIS_DOC = "habilitation"     # Doc.

DEGREE_BC = "Bc."
DEGREE_BSC = "B.Sc."
DEGREE_ING = "Ing."
DEGREE_MGR = "Mgr."
DEGREE_PHD = "PhD."
DEGREE_PHD2 = "Ph.D."
DEGREE_PHDR = "PhDr."
DEGREE_RNDR = "RNDr."
DEGREE_PAEDDR = "PaedDr."
DEGREE_PROF = "prof."
DEGREE_DOC = "doc."
DEGREE_CSC = "CSc."
DEGREE_MBA = "MBA"
DEGREE_DR = "Dr."
DEGREE_MSC = "MSc"
DEGREE_MGA = "MgA."
DEGREE_BCA = "BcA."
DEGREE_DIPLING = "Dipl.-Ing."
DEGREE_ARCH = "arch."         # for Ing. arch.
DEGREE_DIS = "DiS."

# just in case:

DEGREE_MUDR = "MUDr."
DEGREE_MDDR = "MDDr."
DEGREE_MVDR = "MVDr."
DEGREE_JUDR = "JUDr."
DEGREE_THDR = "ThDr."
DEGREE_THD = "Th.D."
DEGREE_THDR = "ThDr."

DEGREES_BC = [
  DEGREE_BC,
  DEGREE_BSC,
  DEGREE_BCA
  ]

DEGREES_MASTER = [
  DEGREE_ING,
  DEGREE_MGR,
  DEGREE_MSC,
  DEGREE_MGA
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
  DEGREE_THDR,
  DEGREE_PAEDDR
  ]

DEGREES = [
  DEGREE_BC,
  DEGREE_BSC,
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
  DEGREE_DR,
  DEGREE_MGA,
  DEGREE_BCA,
  DEGREE_MUDR,
  DEGREE_MDDR,
  DEGREE_MVDR,
  DEGREE_JUDR,
  DEGREE_THDR,
  DEGREE_THD,
  DEGREE_THDR,
  DEGREE_DIPLING,
  DEGREE_ARCH,
  DEGREE_DIS,
  DEGREE_PAEDDR
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

FACULTY_MFF_CUNI    = "MFF CUNI"
FACULTY_FIT_BUT     = "FIT BUT"
FACULTY_FI_MUNI     = "FI MUNI"
FACULTY_FELK_CTU    = "FELK CTU"
FACULTY_FIT_CTU     = "FIT CTU"
FACULTY_FEI_VSB     = "FEI VŠB"
FACULTY_FAI_UTB     = "FAI UTB"
FACULTY_PEF_MENDELU = "PEF MENDELU"

# privates:
FACULTY_UC          = "Unicorn College"
FACULTY_MVSO        = "MVŠO"

# non-CS:
FACULTY_FBMI_CTU    = "FBMI CTU"   # fakulta biomedicinskeho inzenyrstvi
FACULTY_FD_CTU      = "FD CTU"     # fakulta dopravni
FACULTY_FJFI_CTU    = "FJFI CTU"   # fakulta jaderna a fyzikalne inzenyrska
FACULTY_FSV_CTU     = "FSV CTU"    # fakulta stavebni

# branches:

BRANCH_FIT_BUT_BIT   = "FIT BUT BIT"           # (bc) informacni technologie
BRANCH_FIT_BUT_MBS   = "FIT BUT MBS"           # (ing) bezpecnost informacnich technologii
BRANCH_FIT_BUT_MBI   = "FIT BUT MBI"           # (ing) bioinformatika a biocomputing
BRANCH_FIT_BUT_MIS   = "FIT BUT MIS"           # (ing) informacni systemy
BRANCH_FIT_BUT_MIN   = "FIT BUT MIN"           # (ing) inteligentni systemy
BRANCH_FIT_BUT_MMI   = "FIT BUT MMI"           # (ing) management a informacni technologie
BRANCH_FIT_BUT_MMM   = "FIT BUT MMM"           # (ing) matematicke metody v informacnich technologiich
BRANCH_FIT_BUT_MGM   = "FIT BUT MGM"           # (ing) pocitacova grafika a multimedia
BRANCH_FIT_BUT_MPV   = "FIT BUT MPV"           # (ing) pocitacove a vestavene systemy
BRANCH_FIT_BUT_MSK   = "FIT BUT MSK"           # (ing) pocitacove site a komunikace
BRANCH_FIT_BUT_MPS   = "FIT BUT MPS"           # (ing) pocitacove systemy a site

BRANCH_FI_MUNI_MI     = "FI MUNI MI"           # (bc) matematicka informatika
BRANCH_FI_MUNI_PDS    = "FI MUNI PDS"          # (bc/mgr) paralelni a distribuovane systemy
BRANCH_FI_MUNI_GRA    = "FI MUNI GRA"          # (bc/mgr) pocitacova grafika a zpracovani obrazu
BRANCH_FI_MUNI_PSZD   = "FI MUNI PSZD"         # (bc/mgr) pocitacove systemy a zpracovani dat
BRANCH_FI_MUNI_PSK    = "FI MUNI PSK"          # (bc/mgr) pocitacove site a komunikace
BRANCH_FI_MUNI_PTS    = "FI MUNI PTS"          # (bc/mgr) programovatelne technicke struktury
BRANCH_FI_MUNI_UMI    = "FI MUNI UMI"          # (bc/mgr) umela inteligence a zpracovani prirozeneho jazyka
BRANCH_FI_MUNI_AP     = "FI MUNI AP"           # (bc/mgr) aplikovana informatika
BRANCH_FI_MUNI_APGD   = "FI MUNI AP GD"        # (bc/mgr) aplikovana informatika - graficky design
BRANCH_FI_MUNI_BIO    = "FI MUNI BIO"          # (bc/mgr) bioinformatika
BRANCH_FI_MUNI_INVS   = "FI MUNI INVS"         # (bc) informatika ve verejne sprave
BRANCH_FI_MUNI_SOCI   = "FI MUNI SOCI"         # (bc) socialni informatika
BRANCH_FI_MUNI_IO     = "FI MUNI IO"           # (bc) informatika a druhy obor
BRANCH_FI_MUNI_KB     = "FI MUNI KB"           # (mgr) kyberneticka bezpecnost
BRANCH_FI_MUNI_SEC    = "FI MUNI SEC"          # (mgr) security of information and communication technologies
BRANCH_FI_MUNI_IS     = "FI MUNI IS"           # (mgr) informacni systemy
BRANCH_FI_MUNI_TI     = "FI MUNI TI"           # (mgr) teoreticka informatika
BRANCH_FI_MUNI_SSME   = "FI MUNI SSME"         # (mgr) service science, management, and engineering
BRANCH_FI_MUNI_OBR    = "FI MUNI OBR"          # (mgr) zpracovani obrazu
BRANCH_FI_MUNI_UCI    = "FI MUNI UCI"          # (mgr) ucitelstvi informatiky pro stredni skoly

BRANCH_FIT_CTU_BIT    = "FIT CTU BIT"          # (bc) bezpecnost informacnich technologii
BRANCH_FIT_CTU_ISM    = "FIT CTU ISM"          # (bc) studijni obor informacni systemy a management
BRANCH_FIT_CTU_PI     = "FIT CTU PI"           # (bc) pocitacove inzenyrstvi
BRANCH_FIT_CTU_TI     = "FIT CTU TI"           # (bc) teoreticka informatika
BRANCH_FIT_CTU_WSIPG  = "FIT CTU WSI PG"       # (bc) webove inzenyrstvi - pocitacova grafika
BRANCH_FIT_CTU_WSISI  = "FIT CTU WSI SI"       # (bc/ing) webove inzenyrstvi - softwarove inzenyrstvi
BRANCH_FIT_CTU_WSIWI  = "FIT CTU WSI WI"       # (bc/ing) webove inzenyrstvi - webove inzenyrstvi
BRANCH_FIT_CTU_ZI     = "FIT CTU ZI"           # (bc/ing) znalostni inzenyrstvi
BRANCH_FIT_CTU_PB     = "FIT CTU PB"           # (ing) pocitacova bezpecnost
BRANCH_FIT_CTU_PSK    = "FIT CTU PSK"          # (ing) pocitacove systemy a site
BRANCH_FIT_CTU_NPVS   = "FIT CTU NPVS"         # (ing) navrh a programovani vestavenych systemu
BRANCH_FIT_CTU_WSIISM = "FIT CTU WSI ISM"      # (ing) webove inzenyrstvi - informacni systemy a management
BRANCH_FIT_CTU_SPSP   = "FIT CTU SP SP"        # (ing) systemove programovani - systemove programovani
BRANCH_FIT_CTU_SPTI   = "FIT CTU SP TI"        # (ing) systemove programovani - teoreticka informatika
# TODO: FELK branches
                                               # CUNI branches are probably incomplete
BRANCH_MFF_CUNI_IOI   = "MFF CUNI IOI"         # (bc) obecna informatika
BRANCH_MFF_CUNI_IPSS  = "MFF CUNI IPPS"        # (bc) programovani a softwarove systemy
BRANCH_MFF_CUNI_ISDI  = "MFF CUNI ISDI"        # (bc) softwarove a datove inzenyrstvi
BRANCH_MFF_CUNI_IP    = "MFF CUNI IP"          # (bc) programovani
BRANCH_MFF_CUNI_ISPS  = "MFF CUNI ISPS"        # (bc) sprava pocitacovych systemu
BRANCH_MFF_CUNI_IAI   = "MFF CUNI IAI"         # (bc) aplikovana informatika
BRANCH_MFF_CUNI_IML   = "MFF CUNI IML"         # (mgr) matematicka lingvistika
BRANCH_MFF_CUNI_ITI   = "MFF CUNI ITI"         # (mgr) teoreticka informatika
BRANCH_MFF_CUNI_IDI   = "MFF CUNI IDI"         # (mgr) datove inzenyrstvi
BRANCH_MFF_CUNI_ISS   = "MFF CUNI ISS"         # (mgr) softwarove systemy
BRANCH_MFF_CUNI_MMIB  = "MFF CUNI MMIB"        # (mgr) matematicke metody informacni bezpecnosti

BRANCH_FAI_UTB_ISR    = "FAI UTB ISR"          # (bc) inteligentni systemy s roboty
BRANCH_FAI_UTB_SWI    = "FAI UTB SWI"          # (bc) softwarove inzenyrstvi
BRANCH_FAI_UTB_IRT    = "FAI UTB IŘT"          # (bc) informacni a ridici technologie
BRANCH_FAI_UTB_ITA    = "FAI UTB ITA"          # (bc) informacni technologie v administrative
BRANCH_FAI_UTB_BTSM   = "FAI UTB BTSM"         # (bc/ing) bezpecnostni technologie, systemy a management
BRANCH_FAI_UTB_ARI    = "FAI UTB AŘI"          # (ing) automaticke rizeni a informatika
BRANCH_FAI_UTB_IT     = "FAI UTB IT"           # (ing) informacni technologie
BRANCH_FAI_UTB_ISB    = "FAI UTB ISB"          # (ing) integrovane systemy v budovach
BRANCH_FAI_UTB_PKS    = "FAI UTB PKS"          # (ing) pocitacove a komunikacni systemy
BRANCH_FAI_UTB_UISS   = "FAI UTB UISŠ"         # (ing) ucitelstvi informatiky pro stredni skoly

BRANCH_FEI_VSB_RIS    = "FEI VŠB RIS"          # (bc/ing) ridici a informacni systemy
BRANCH_FEI_VSB_IVT    = "FEI VŠB IVT"          # (bc/ing) informacni a vypocetni technika
BRANCH_FEI_VSB_MT     = "FEI VŠB MT"           # (bc/ing) mobilni technologie
BRANCH_FEI_VSB_TT     = "FEI VŠB TT"           # (bc/ing) telekomunikacni technika
BRANCH_FEI_VSB_VM     = "FEI VŠB VM"           # (bc/ing) vypocetni matematika
BRANCH_FEI_VSB_IKB    = "FEI VŠB IKB"          # (ing) informacni a komunikacni bezpecnost

# departments:

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

DEPARTMENT_FI_MUNI_KPSK = "KPSK FI MU"       # katedra pocitacovych systemu a komunikace
DEPARTMENT_FI_MUNI_CVT = "CVT FI MU"         # centrum vypocetni techniky
DEPARTMENT_FI_MUNI_KPGD = "KPGD FI MU"       # katedra pocitacove grafiky a designu
DEPARTMENT_FI_MUNI_KIT = "KIT FI MU"         # katedra informacnich technologii
DEPARTMENT_FI_MUNI_KTP = "KTP FI MU"         # katedra teorie programovani

DEPARTMENT_FF_MUNI_UHV = "ÚHV FF MU"         # ustav hudebni vychovy
DEPARTMENT_PDF_MUNI_KTECH = "KTechV PdF MU"  # katedra technicke a informacni vychovy
DEPARTMENT_FF_MU_UCJ = "ÚČJ FF MU"           # ustav ceskeho jazyka

DEPARTMENTS_MUNI = [
  DEPARTMENT_FI_MUNI_KPSK,
  DEPARTMENT_FI_MUNI_CVT,
  DEPARTMENT_FI_MUNI_KPGD,
  DEPARTMENT_FI_MUNI_KIT,
  DEPARTMENT_FI_MUNI_KTP,
  DEPARTMENT_FF_MUNI_UHV,
  DEPARTMENT_PDF_MUNI_KTECH,
  DEPARTMENT_FF_MU_UCJ
]

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
  "klasifikace": FIELD_AI,
  "computability": FIELD_TCS,
  "decidability": FIELD_TCS,
  "QoS": FIELD_NET
  }

KEYWORDS_TO_FIELD_LOWER = {}

for k in KEYWORDS_TO_FIELD:
  KEYWORDS_TO_FIELD_LOWER[k.lower()] = KEYWORDS_TO_FIELD[k]

CITY_PRAHA = "Praha"
CITY_BRNO = "Brno"
CITY_OSTRAVA = "Ostrava"
CITY_ZLIN = "Zlín"

SYSTEM_LATEX = "LaTeX"
SYSTEM_WORD = "MS Word"
SYSTEM_OPEN_OFFICE = "Open Office"
SYSTEM_TYPEWRITER = "typewriter"
SYSTEM_GHOSTSCRIPT = "ghostscript"
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
  "Dávid", "Samuel", "Mohamed", "Moslem", "Gabriel",
  "Zdeněk","Lubor","Matúš","Marian","Ľubomír","Ján",
  "Ondrej","Peter","Vratislav","Zdenek","Jeroným",
  "Vladan","Matouš","Andrzej","Boris","Zdeněk",
  "Viliam","Jonáš","Leo","Artur","Pavol","Boleslav",
  "Bohdan","Patrick","Ota","Věroslav","Antonín",
  "Vlastimil","Karol","Rastislav","Kristián","Rostislav",
  "Johny","Bohdan","Zdenko","Slavomír","Fedor","Řehoř",
  "Bruno","Lačezar","Vilém","Matyáš","Cyril","Karel",
  "Leonard","Aleksei"]

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

PROXIES = [
    "109.169.6.152:8080",
    "123.231.65.170:8080",
    "79.137.24.195:3128",
    "175.45.132.96:80",
    "46.105.50.151:8080",
    "119.226.14.46:80",
    "149.255.154.4:8080",
    "194.88.105.156:3128",
    "51.255.48.61:8080",
    "212.237.12.18:1189",
    "89.36.212.129:1189",
    "205.196.181.11:8080",
    "45.32.139.160:3128",
    "24.244.168.15:8080",
    "190.90.162.98:53281",
    "78.26.207.173:53281",
    "36.37.221.184:53281",
    "87.119.236.208:53281",
    "62.122.65.60:53281",
    "51.15.66.2:3128",
    "203.130.2.66:53281",
    "142.165.19.133:3128",
    "186.42.191.166:53281",
    "105.28.119.228:8080",
    "78.156.49.241:53281",
    "45.58.124.164:1080",
    "111.68.115.22:53281",
    "103.248.233.156:80",
    "109.169.6.152:8080",
    "24.244.168.13:8080",
    "189.99.227.231:8080",
    "52.144.46.176:8080",
    "45.32.163.55:3128",
    "45.58.124.166:1080",
    "100.12.34.36:8080",
    "45.58.124.164:1080",
    "68.11.154.37:53281",
    "45.58.124.166:1080",
    "23.94.102.180:1080",
    "23.94.102.178:1080",
    "170.55.15.175:3128",
    "23.94.102.179:1080",
    None
  ]

def guess_field_from_keywords(keyword_list):
  if keyword_list == None:
    return None

  histogram = {}

  for field in ALL_FIELDS:
    histogram[field] = 0

  for keyword in keyword_list:
    if keyword != None and keyword.lower() in KEYWORDS_TO_FIELD_LOWER:
      histogram[KEYWORDS_TO_FIELD_LOWER[keyword.lower()]] += 1

  best_field = None
  best_score = 0

  for field in histogram:
    if histogram[field] > best_score:
      best_field = field
      best_score = histogram[field]

  return best_field

def degree_to_thesis_type(degree): 
  if degree in DEGREES_BC:
    return THESIS_BACHELOR
  elif degree in DEGREES_MASTER:
    return THESIS_MASTER
  elif degree in DEGREES_PHD:
    return THESIS_PHD
  elif degree in DEGREES_DR:
    return THESIS_DR
  elif degree == DEGREE_DOC:
    return THESIS_DOC

  return None

class Person(object):
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
 
    parts = filter(lambda item: item not in DEGREES and item != "et",parts)  # et for Ing. et Ing. etc.

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

class Thesis(object):
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
    self.public_university = None
    self.branch = None
    self.note = None

  def __str__(self):
    return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4, ensure_ascii=False)

  def handle_branch(self, branch_string, substring_mapping):
    for substr in substring_mapping:
      if branch_string.find(substr) >= 0:
        self.branch = substring_mapping[substr]
        break

  def incorporate_pdf_info(self, pdf_info):
    self.pages = pdf_info.pages
    self.size = pdf_info.size    
    self.typesetting_system = pdf_info.typesetting_system

    if self.language == None:
      self.language = pdf_info.language

  def normalize(self):              # makes the object consistent
    def print_norm(print_what):
      print("NORMALIZATION: " + str(print_what))

    if self.opponents == None:
      print_norm("correcting oppoentnts (None to [])")
      self.opponents = []

    self.opponents = filter(lambda item: item != None and isinstance(item,Person),self.opponents)

    if self.keywords == None: 
      print_norm("correcting keywords (None to [])")
      self.keywords = []

    try:
      self.abstract_cs = self.abstract_cs.replace("\n"," ").rstrip().lstrip()
      self.abstract_en = self.abstract_en.replace("\n"," ").rstrip().lstrip()
    except Exception:
      pass

    self.keywords = beautify_list(filter(lambda item: item != None,self.keywords))

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
   
    if self.degree in DEGREES_BC and self.kind != THESIS_BACHELOR:
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

    if self.pages != None and not type(self.pages) is int:
      print_norm("number of pages not int - correcting")

      try:
        self.pages = int(self.pages)
      except Exception:
        self.pages = None

    if self.year != None and not type(self.year) is int:
      print_norm("year not int - correcting")
      
      try:
        self.year = int(self.year)

        if self.year < 1000 or self.year > 3000:
          print_norm("wrong year value (" + str(self.year) + ") - clearing")
          self.year = None

      except Exception:
        print_norm("could not convert year to int")

    if self.faculty in (FACULTY_FIT_BUT,FACULTY_FIT_CTU,FACULTY_FELK_CTU,
      FACULTY_FAI_UTB,FACULTY_MFF_CUNI,FACULTY_FEI_VSB,FACULTY_FI_MUNI) and self.public_university != True:
      print_norm("public university but public_university != True - correcting")
      self.public_university = True

class PDFInfo(object):
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

      self.size = os.path.getsize(filename)

      self.pages = input_pdf.getNumPages()
     
      self.pdf_text = ""

      for page in range(self.pages):
        self.pdf_text += input_pdf.getPage(page).extractText()

      self.characters = len(self.pdf_text)

      self.language = langdetect.detect(self.pdf_text)    # we suppose page 10 exists and has some text

      if input_pdf.getDocumentInfo().creator != None:
        created_with = input_pdf.getDocumentInfo().creator
      else:
        created_with = input_pdf.documentInfo["/Producer"]

      if created_with[:5].lower() == "latex":
        self.typesetting_system = SYSTEM_LATEX
      elif created_with.lower().find("word") >= 0:
        self.typesetting_system = SYSTEM_WORD 
      elif created_with.lower().find("writer") >= 0:
        self.typesetting_system = SYSTEM_OPEN_OFFICE
      elif created_with.lower().find("ghostscript") >= 0:
        self.typesetting_system = SYSTEM_GHOSTSCRIPT
      else:
        self.typesetting_system = SYSTEM_OTHER

    except Exception as e:
      print("could not analyze PDF: " + str(e))

def beautify_list(keywords):  # removes duplicates, empties, strips etc.
  return [item.decode("utf-8") for item in
    map(lambda s: s.lstrip().rstrip(),
      filter(lambda item: item != None,list(set(keywords)))) if len(item) > 1]

def download_webpage(url,encoding="utf-8",try_proxy=True):
  if try_proxy:
    random_proxy = random.choice(PROXIES)
  else:
    random_proxy = None

  wait_for = 30.0

  if random_proxy != None:
    proxies = { "http": random_proxy, "https": random_proxy }
    r = requests.get(url, proxies=proxies, verify=False, timeout=wait_for)
  else:
    r = requests.get(url, verify=False, timeout=wait_for)

  r.encoding = encoding
  return r.text

def download_to_file(url, filename):
  gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
  web_file = urllib2.urlopen(url,context=gcontext,timeout=120)

  with open(filename,"wb") as local_file:
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

def grade_to_number(grade):
  if grade == GRADE_A:
    return 1.0
  elif grade == GRADE_B:
    return 1.5
  elif grade == GRADE_C:
    return 2.0
  elif grade == GRADE_D:
    return 2.5
  elif grade == GRADE_E:
    return 3.0
  else:
    return 4.0

def person_to_string(person):
  if person == None:
    return "none"

  result = ""

  degrees_after = []

  for degree in person["degrees"]:
    if degree in DEGREES_AFTER:
      degrees_after.append(degree)
    else:
      result += degree + " "

  result += str(person["name_first"]) + " " + str(person["name_last"])

  for degree in degrees_after:
    result += " " + degree

  return result

def thesis_to_string(thesis, lang="cs"):
  if thesis == None:
    return "none"

  result = ""

  if thesis["author"] != None:
    result += person_to_string(thesis["author"]) + ": "

  other_lang = "en" if lang == "cs" else "cs"

  result += str(thesis["title_" + lang] if thesis["title_" + lang] != None else thesis["title_" + other_lang])

  if thesis["year"] != None:
    result += ", " + str(thesis["year"])

  if thesis["faculty"] != None:
    result += ", " + thesis["faculty"]

  if thesis["kind"] != None:
    result += ", " + thesis["kind"] + " thesis"

  if thesis["pages"] != None:
    result += ", " + str(thesis["pages"]) + " pages"

  if thesis["size"] != None:
    result += ", " + "{0:.2f}".format(thesis["size"] / 1000000.0) + " MB"

  return result

def load_json(filename):
  text = get_file_text(filename)
  return json.loads(text,encoding="utf8")

def save_json(what, filename):
  f = open(filename,"w")
  f.write(json.dumps(what,sort_keys=True,ensure_ascii=False,indent=1))
  f.close()

reload(sys)
sys.setdefaultencoding("utf8")
