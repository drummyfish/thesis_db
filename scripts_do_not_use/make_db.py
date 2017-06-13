#!/usr/bin/env python
# -*- coding: utf-8 -*-

# BEWARE!!! This script doesn't work out of the box, so don't just run it.
# It only provides tools for downloading theses.

from common import *

reload(sys)
sys.setdefaultencoding("utf8")

def debug_print(print_string):
  print("DEBUG: " + print_string)
  sys.stdout.flush()

def progress_print(print_string):
  print("PROGRESS: " + print_string)
  sys.stdout.flush()

def iterative_load(soup,find_func,process_func):
  result = []

  current = soup.find("body").find_next(find_func)

  while current != None:
    result.append(process_func(current))
    current = current.find_next(find_func)

  return result

class FacultyDownloader(object):      # base class for downloaders of theses of a single faculty
  def get_thesis_list(self):          # get list of links to thesis pages
    return []

  def get_thesis_info(self,url):
    return Thesis()

#----------------------------------------

class FitButDownloader(FacultyDownloader):

  BASE_URL = "http://www.fit.vutbr.cz/"

  def get_thesis_info(self, url): 
    result = Thesis()
    result.public_university = True

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
    soup = BeautifulSoup(download_webpage(url.replace(".php",".php.cs",1),"ISO-8859-2"),"lxml")
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

    try:
      if result.kind == THESIS_DOC:
        result.author = Person(soup.find("h2",string="Habilitace").find_next("a").string,False)
      else:
        result.author = person_from_table(u"Student:")
        result.supervisor = person_from_table(u"Vedoucí:")
    except Exception as e:
      debug_print("could not resolve author/supervisor:" + str(e))

    if result.kind != THESIS_PHD:
      result.opponents = [person_from_table(u"Oponent:")]

    try:
      if result.kind == THESIS_PHD:
        result.year = int(text_in_table(u"Disertace:"))
      elif result.kind == THESIS_DOC:
        result.year = int(text_in_table(u"Rok:"))
      else: 
        result.year = int(text_in_table(u"Ak.rok:").split("/")[1])
    except Exception as e:
      debug_print("year not found: " + str(e))
 
    try:
      if result.kind == THESIS_BACHELOR:
        result.branch = BRANCH_FIT_BUT_BIT     # only one branch for Bc.
      elif result.kind == THESIS_MASTER:
        branch_string = text_in_table("Obor studia:")     

        substring_to_branch = {
          "MGM": BRANCH_FIT_BUT_MGM,
          "MBS": BRANCH_FIT_BUT_MBS,
          "MBI": BRANCH_FIT_BUT_MBI,
          "MMM": BRANCH_FIT_BUT_MMM,
          "MIS": BRANCH_FIT_BUT_MIS,
          "MIN": BRANCH_FIT_BUT_MIN,
          "MPV": BRANCH_FIT_BUT_MPV,
          "MSK": BRANCH_FIT_BUT_MSK,
          "MPS": BRANCH_FIT_BUT_MPS,
          "MMI": BRANCH_FIT_BUT_MMI
          }

        result.handle_branch(branch_string,substring_to_branch) 
  
    except Exception as e:
      debug_print("could not resolve branch: " + str(e))

    try:
      branch_string = text_in_table(u"Obor studia:")

      prefix_fields = (
        (u"Bezpečnost",             FIELD_SEC),
        (u"Počítačová grafika",     FIELD_CG),
        (u"Informační systémy",     FIELD_IS),
        (u"Počítačové a vestavěné", FIELD_HW),
        (u"Inteligentní",           FIELD_AI),
        (u"Počítačové sítě",        FIELD_NET),
        (u"Bioinformatika",         FIELD_BIO),
        ("Management",              FIELD_MAN)
        )

      for item in prefix_fields:
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
         soup.find("th",string="Klíčová slova").find_next(lambda t: t.string != None).string.split(",") +
         soup_en.find("th",string="Keywords").find_next(lambda t: t.string != None).string.split(",")
         )
    except Exception as e:
      debug_print("keywords not found:" + str(e)) 

    if result.field == None:
      result.field = guess_field_from_keywords(result.keywords)

    if result.field == None and result.department == DEPARTMENT_FIT_BUT_UPGM:
      result.field = FIELD_CG
   
    try: 
      if result.kind == THESIS_DOC:
        result.abstract_cs = text_in_table("Anotace")
        result.abstract_en = text_in_table("Annotation",False)
      else: 
        result.abstract_cs = text_in_table("Abstrakt")
        result.abstract_en = text_in_table("Abstract",False)
    except Exception as e:
      debug_print("could not extract abstract:" + str(e))

    result.url_page = url

    try:
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
    except Exception as e: 
      debug_print("error with fulltext/defended/grade: " + str(e))

    try:
      if result.kind == THESIS_DOC:
        lang_string = text_in_table("Jazyk publikace:")  
      else:
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
      if result.kind == THESIS_DOC:
        title_string = text_in_table("Název publikace:")

        if result.language == None:
          result.language = langdetect(title_string)

          if not result.language in (LANGUAGE_CS,LANGUAGE_SK,LANGUAGE_EN):
            result.language = None

        if result.language != LANGUAGE_EN:
          result.title_cs = title_string
          result.title_en = text_in_table("Název (en):")
        else:
          result.title_en = title_string
          result.title_cs = text_in_table("Název (cs):")
      else:
        result.title_en = soup_en.find("h2").string
        result.title_cs = soup.find("h2").string

        if result.title_cs == result.title_en:
          likely_title_language = langdetect.detect(result.title_cs)

          if likely_title_language == "cs":
            result.title_en = None
          elif likely_title_language == "en":
            result.title_cs = None 

    except Exception as e:
      debug_print("could not resolve title(s):" + str(e))

    try:
      pdf_info = download_and_analyze_pdf(result.url_fulltext) 
      result.incorporate_pdf_info(pdf_info)

    except Exception as e:
      debug_print("pdf could not be analyzed: " + str(e))

    try:
      if result.pages == None:
        result.pages = int(text_in_table("Strany:")) 
    except Exception:
      pass

    result.normalize() 
    return result

  def get_thesis_list(self):
    result = []

    for thesis_type in ["BP","DP","PD","DOC"]:
      progress_print("downloading FIT BUT list for " + thesis_type)

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

class CtuDownloader(FacultyDownloader):      # for FEI and FELK don't forget to get extra theses with get_others

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
        progress_print("downloading other thesis, CTU")

        try:
          current = current.find_next("td")
          
          if current == None:
            break

          if state == 0:    # author
            result.append(Thesis())

            result[-1].defended = True
            result[-1].defended = CITY_PRAHA
            result[-1].public_university = True
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

              if other_type == 1:
                result[-1].url_fulltext = "https://www.fit.cvut.cz" + result[-1].url_fulltext 
 
            try:
              if result[-1].url_fulltext != None:
                pdf_info = download_and_analyze_pdf(result[-1].url_fulltext)
                result[-1].incorporate_pdf_info(pdf_info)
            except Exception:
              debug_print("could not download pdf")

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
        except Exception as e:
          debug_print("there was an error: " + str(e))

    return result

  def get_thesis_list(self):
    result = []

    for faculty in ("F8","F3"):
      departments = range(101,106) if faculty == "F8" else (13136,13139)

      for department in departments:
        progress_print("downloading CTU thesis list for " + faculty + " " + str(department))

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
    result.public_university = True

    # branch info is unavailable at the CTU website

    soup = BeautifulSoup(download_webpage(url,"ISO-8859-2"),"lxml")
 
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
   
    try:
      result.department = string_to_department[text_in_table("katedra")]
    except Exception as e:
      debug_print("could not resolve department: " + str(e))

    result.field = department_to_field[result.department]
 
    try:
      result.author = Person(text_in_table("autor"))
      result.supervisor = Person(text_in_table("vedoucí"))
      result.year = int(text_in_table("rok"))
      type_string = text_in_table("typ")

      if type_string == "Diplomová práce":
        result.kind = THESIS_MASTER
        result.degree = DEGREE_ING
      elif type_string == "Bakalářská práce":
        result.kind = THESIS_BACHELOR
        result.degree = DEGREE_BC

    except Exception as e:
      debug_print("error at author/supervisor/year/type: " + str(e))

    if type_string == "Diplomová práce":
      result.kind = THESIS_MASTER
      result.degree = DEGREE_ING
    elif type_string == "Bakalářská práce":
      result.kind = THESIS_BACHELOR
      result.degree = DEGREE_BC

    try:
      result.title_en = text_in_table("název (anglicky)")
      result.title_cs = text_in_table("název")
    except Exception as e:
      debug_print("could not resolve title: " + str(e))

    try:
      result.abstract_en = text_in_table("abstrakt (anglicky)")
      result.abstract_cs = text_in_table("abstrakt")
    except Exception as e:
      debug_print("could not resolve abstract: " + str(e))

    try:
      result.url_fulltext = CtuDownloader.BASE_URL + soup.find("td",string="fulltext").find_next("a")["href"]  
    except Exception as e:
      debug_print("could not resolve fulltext: " + str(e))

    try:
      pdf_info = download_and_analyze_pdf(result.url_fulltext)
      result.incorporate_pdf_info(pdf_info)
    except Exception as e:
      debug_print("could not analyze pdf: " + str(e))

    result.normalize() 
    return result

#----------------------------------------

class CtuExtraDownloader(FacultyDownloader):     # downloads theses from Ctu faculties other than FEI and FELK

  BASE_URL = "https://dspace.cvut.cz/"

  def get_thesis_list(self):
    result = []

    urls = [ 
        "https://dspace.cvut.cz/handle/10467/3560",
        "https://dspace.cvut.cz/handle/10467/19149",
        "https://dspace.cvut.cz/handle/10467/3478",
        "https://dspace.cvut.cz/handle/10467/19143",
        "https://dspace.cvut.cz/handle/10467/3320",
        "https://dspace.cvut.cz/handle/10467/2948"
      ] 

    page_links = []

    for url in urls:
      soup = BeautifulSoup(download_webpage(url),"lxml")

      bp_link = CtuExtraDownloader.BASE_URL[:-1] + soup.find(lambda t: t.name == "span" and t.string != None and starts_with(t.string,"Bakalářské práce")).parent["href"]
      dp_link = CtuExtraDownloader.BASE_URL[:-1] + soup.find(lambda t: t.name == "span" and t.string != None and starts_with(t.string,"Diplomové práce")).parent["href"]

      page_links += [bp_link,dp_link]

    for page_link in page_links:
      progress_print("downloading extra CTU list for " + page_link)
      current_url = page_link

      while True: 
        soup = BeautifulSoup(download_webpage(current_url),"lxml")

        result += iterative_load(soup,
            lambda t: t.name == "a" and t.parent.name == "h4",
            lambda t: CtuExtraDownloader.BASE_URL[:-1] + t["href"]
          )

        current_url = soup.find("a",class_="next-page-link")

        if current_url == None or current_url["href"] == "":
          break
      
        current_url = CtuExtraDownloader.BASE_URL[:-1] + current_url["href"]

    return result

  def get_thesis_info(self, url):
    result = Thesis()
    result.url_page = url
    result.city = CITY_PRAHA
    result.public_university = True

    url += "?show=full"

    soup = BeautifulSoup(download_webpage(url),"lxml")

    def text_in_table(line):
      return soup.find("td",string=line).find_next("td").string

    try:
      result.author = Person(text_in_table("dc.contributor.author"),False)
      result.supervisor = Person(text_in_table("dc.contributor.advisor"),False)
      result.opponents = [Person(text_in_table("dc.contributor.referee"),False)]
    except Exception as e:
      debug_print("error at author/supervisor/opponent: " + str(e))

    try:
      result.degree = text_in_table("theses.degree.name")
      result.kind = degree_to_thesis_type(result.degree)
    except Exception as e:
      debug_print("could not resolve degree/type: " + str(e))

      try:
        type_string = text_in_table("dc.type")

        if type_string == "MAGISTERSKÁ PRÁCE":
          result.kind = THESIS_MASTER
        elif type_string == "BAKALÁŘSKÁ PRÁCE":
          result.kind = THESIS_BACHELOR
          result.degree = DEGREE_BC
      except Exception:
        pass

    try:
      result.language = text_in_table("dc.language.iso")
      
      if result.language.lower() == "eng":
        result.language = LANGUAGE_EN
      elif result.language.lower() == "cze":
        result.language = LANGUAGE_CS
      if result.language.lower() == "svk":
        result.language = LANGUAGE_SK
    except Exception as e:
      debug_print("could not resolve language: " + str(e))
 
    try:
      t1 = soup.find("td",string="dc.title")
      t2 = t1.find_next("td",string="dc.title")

      result.title_cs = t1.find_next("td").string
      result.title_en = t2.find_next("td").string
    except Exception as e:
      debug_print("could not resolve title: " + str(e))

    try:
      result.url_fulltext = CtuExtraDownloader.BASE_URL[:-1] + soup.find(lambda t: t.name == "dd" and t.get("title") == "PLNY_TEXT").find_next("a")["href"]
    except Exception as e:
      debug_print("could not resolve fulltext: " + str(e))

    try:
      result.year = int(text_in_table("dc.date.issued").split("-")[0])
    except Exception as e:
      debug_print("could not resolve year: " + str(e))

    try:
      faculty_string = text_in_table("theses.degree.grantor")

      if faculty_string.find("biomedicín") >= 0:
        result.faculty = FACULTY_FBMI_CTU
      elif faculty_string.find("doprav") >= 0:
        result.faculty = FACULTY_FD_CTU
      elif faculty_string.find("jader") >= 0 or faculty_string.find("softwarového") >= 0: 
        result.faculty = FACULTY_FJFI_CTU
      elif faculty_string.find("staveb") >= 0:
        result.faculty = FACULTY_FSV_CTU

    except Exception as e:
      debug_print("could not resolve faculty: " + str(e))

    try:
      keywords = iterative_load(soup,
        lambda t: t.name == "td" and t.string != None and t.string == "dc.subject",
        lambda t: t.find_next("td").string)

      helper = []
 
      for k in keywords:
        for k2 in k.replace(",","").split(" "):
          helper.append(k2)

      result.keywords = beautify_list(helper)
    except Exception as e:
      debug_print("could not resolve keywords: " + str(e))

    try:
      a1 = soup.find("td",string="dc.description.abstract")
      a2 = a1.find_next("td",string="dc.description.abstract")

      result.abstract_cs = a1.find_next("td").string
      result.abstract_en = a2.find_next("td").string
    except Exception as e:
      debug_print("could not resolve abstract: " + str(e))

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
      progress_print("downloading FAI UTB list for " + str(l[2]))

      offset = 0

      while True:    # for each page
        progress_print("offset " + str(offset))

        soup = BeautifulSoup(download_webpage("http://digilib.k.utb.cz/handle/10563/" + str(l[2]) + "/recent-submissions?offset=" + str(offset)),"lxml")

        links = iterative_load(soup,
          lambda t: t.name == "a" and t.next_sibling != None and t["href"].find("=") == -1 and t["href"][:3] == "/ha" and t.parent.name == "div",
          lambda t: FaiUtbDownloader.BASE_URL + t["href"][1:],
          )

        result += links

        offset += 20

        if soup.find("a",class_="next-page-link") == None or len(links) == 0 or offset > 20000:
          break

    return result

  def get_thesis_info(self, url):
    result = Thesis()
    result.url_page = url
    result.city = CITY_ZLIN
    result.public_university = True

    url += "?show=full"

    result.faculty = FACULTY_FAI_UTB

    soup =  BeautifulSoup(download_webpage(url),"lxml")

    def text_in_table(line):
      tag = soup.find("td",string=line).find_next("td")
      return tag.string if tag.string != None else tag.contents[1].string

    try:
      result.year = int(text_in_table("dc.date.issued").split("-")[0])
    except Exception as e:
      debug_print("could not resolve year: " + str(e))

    try:
      result.author = Person(text_in_table("dc.contributor.author"),False)
    except Exception as e:
      debug_print("could not resolve author: " + str(e))

    try:
      result.supervisor = Person()
      result.supervisor.from_string(text_in_table("dc.contributor.advisor"),False)
    except Exception as e:
      result.supervisor = None 
      debug_print("supervisor not found: " + str(e))

    try:
      result.language = text_in_table("dc.language.iso")
    except Exception as e:
      debug_print("could not resolve language: " + str(e))

    try:
      result.degree = text_in_table("dc.thesis.degree-name")
      result.kind = degree_to_thesis_type(result.degree)
    except Exception as e:
      debug_print("could not resolve degree: " + str(e))

    try:
      if result.kind != THESIS_PHD:
        result.grade = text_in_table("utb.result.grade")
    except Exception as e:
      debug_print("grade not found: " + str(e))

    if result.grade in (GRADE_A, GRADE_B, GRADE_C, GRADE_D, GRADE_E):
      result.defended = True
    elif result.grade == GRADE_F:
      result.defended = False

    try:
      result.title_cs = text_in_table("dc.title")
      result.title_en = text_in_table("dc.title.alternative")
    except Exception as e:
      debug_print("could not resolve title: " + str(e))

    if result.title_cs == result.title_en:
      result.title_cs = None

    try:
      result.abstract_cs = text_in_table("dc.description.abstract")
      result.abstract_en = text_in_table("dc.description.abstract-translated")
    except Exception as e:
      debug_print("abstract not found: " + str(e))

    result.opponents = iterative_load(soup,
      lambda t: t.name == "td" and t.string == "dc.contributor.referee",
      lambda t: Person(t.find_next("td").string,False)
      )
   
    result.keywords = beautify_list(iterative_load(soup,
      lambda t: t.name == "td" and t.string == "dc.subject",
      lambda t: t.find_next("td").contents[1].string))

    try:
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
    except Exception as e:
      debug_print("department not found: " + str(e))

    try:
      branch_string = text_in_table("dc.thesis.degree-discipline")

      substring_to_branch = {
        "Informační technologie": BRANCH_FAI_UTB_IT,
        "Bezpečnostní technologie": BRANCH_FAI_UTB_BTSM,
        "řídicí technologie": BRANCH_FAI_UTB_IRT,
        "v administrativě": BRANCH_FAI_UTB_ITA,
        "Automatizace a řídicí": BRANCH_FAI_UTB_ARI,
        "Učitelství": BRANCH_FAI_UTB_UISS,
        "komunikační systémy": BRANCH_FAI_UTB_PKS, 
        "roboty": BRANCH_FAI_UTB_ISR,
        "Softwarové": BRANCH_FAI_UTB_SWI,
        "budovách": BRANCH_FAI_UTB_ISB 
        }

      result.handle_branch(branch_string,substring_to_branch)
    except Exception as e:
      debug_print("could not resolve branch: " + str(e))

    if result.field == None:
      result.field = guess_field_from_keywords(result.keywords)
    
    try:
      result.url_fulltext = FaiUtbDownloader.BASE_URL + soup.find("table",class_="ds-table file-list").find_next("a")["href"] 

      if result.url_fulltext.find(".pdf") >= 0:
        pdf_info = download_and_analyze_pdf(result.url_fulltext)
        result.incorporate_pdf_info(pdf_info)
    except Exception as e:
      debug_print("error at fulltext: " + str(e))

    result.normalize() 
    return result

#---------------------------------------

class MffCuniDownloader(FacultyDownloader):

  def get_thesis_info(self, url):
    result = Thesis()

    result.city = CITY_PRAHA
    result.faculty = FACULTY_MFF_CUNI
    result.url_page = url
    result.public_university = True

    soup = BeautifulSoup(download_webpage(url),"lxml")

    def text_in_table(line):
      return soup.find(lambda t: t.name == "div" and t.string != None and t.string.lstrip().rstrip() == line).find_next("span").string.lstrip().rstrip()

    branch_string = text_in_table("Obor studia:")

    substring_to_branch = {
      "IOI": BRANCH_MFF_CUNI_IOI,
      "IPSS": BRANCH_MFF_CUNI_IPSS,
      "ISDI": BRANCH_MFF_CUNI_ISDI,
      "IP": BRANCH_MFF_CUNI_IP,
      "ISPS": BRANCH_MFF_CUNI_ISPS,
      "IAI": BRANCH_MFF_CUNI_IAI,
      "IML": BRANCH_MFF_CUNI_IML,
      "ITI": BRANCH_MFF_CUNI_ITI,
      "IDI": BRANCH_MFF_CUNI_IDI,
      "ISS": BRANCH_MFF_CUNI_ISS,
      "MMIB": BRANCH_MFF_CUNI_MMIB,
      }

    result.handle_branch(branch_string,substring_to_branch)

    if result.branch != BRANCH_MFF_CUNI_MMIB:        # only allowed non-cs branch
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
      result.abstract_cs = text_in_table("Abstrakt:").replace("\n"," ")   
      result.abstract_en = text_in_table("Abstract v angličtině:").replace("\n"," ")   
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

    result.kind = degree_to_thesis_type(result.degree)

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
    result.incorporate_pdf_info(pdf_info)

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
      progress_print("downloading MFF CUNI list, page " + str(page))

      soup = BeautifulSoup(download_webpage("https://is.cuni.cz/webapps/zzp/search/?______searchform___search=&______facetform___facets___faculty%5B%5D=11320&tab_searchas=basic&lang=cs&PSzzpSearchListbasic=10&SOzzpSearchListbasic=&_sessionId=0&______searchform___butsearch=Vyhledat&PNzzpSearchListbasic=" + str(page)),"lxml")

      current = soup.find("span",class_="title")

      links = iterative_load(soup,
        lambda t: t.name == "div" and t.get("class") != None and t.get("class")[0] == "zzp-work-maintitle",
        lambda t: t.contents[1]["href"]
        )

      result += links

      page += 1

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
      progress_print("downloading FEI VSB thesis list, offset " + str(offset))      

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
    result.public_university = True

    result.url_page = url

    result.faculty = FACULTY_FEI_VSB
    result.city = CITY_OSTRAVA

    soup =  BeautifulSoup(download_webpage(url),"lxml")

    def text_in_table(line):
      return soup.find("td",string=line).find_next("td").string

    try:
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
    except Exception as e:
      debug_print("could not resolve thesis type:" + str(e))

    try:
      result.author = Person(text_in_table("dc.contributor.author"),False)
      result.supervisor = Person(text_in_table("dc.contributor.advisor"),False)
      result.year = int(text_in_table("dc.date.issued"))
      result.language = text_in_table("dc.language.iso")
    except Exception as e:
      debug_print("error at author/supervisor/year/language: " + str(e))   

    try:
      branch_string = text_in_table("dc.thesis.degree-branch")

      substring_to_branch = {
        "Informatika a": BRANCH_FEI_VSB_IVT,
        "Řídicí": BRANCH_FEI_VSB_RIS,
        "Mobilní": BRANCH_FEI_VSB_MT,
        "Telekomuni": BRANCH_FEI_VSB_TT,
        "Výpočetní mat": BRANCH_FEI_VSB_VM,
        "komunikační bezpečnost": BRANCH_FEI_VSB_IKB
        }

      result.handle_branch(branch_string,substring_to_branch)
    except Exception as e:
      debug_print("could not recolve branch: " + str(e))

    try:
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
    except Exception as e:
      debug_print("could not resolve title: " + str(e))

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

    # fulltexts are not available for FEI VSB

    try:
      result.pages = int(text_in_table("dc.format").split(" ").replace(",","")[0])
    except Exception as e:
      debug_print("could not retrieve number of pages: " + str(e))

    result.normalize() 
    return result

#----------------------------------------

class FiMuniDownloader(FacultyDownloader):   # don't forget to get more theses with get_others (after calling get_thesis_list)

  BASE_URL = "https://is.muni.cz/"

  def __init__(self):
    super(FiMuniDownloader,self).__init__()

    self.other_theses_retrieved = False
    self.other_theses = []

    self.substring_to_branch = {
        "Zpracování": BRANCH_FI_MUNI_OBR,
        "Aplikovaná": BRANCH_FI_MUNI_AP,
        "Teoretická": BRANCH_FI_MUNI_TI,
        "grafika": BRANCH_FI_MUNI_GRA,
        "Informační systémy": BRANCH_FI_MUNI_IS,
        "Matematická": BRANCH_FI_MUNI_MI,
        "Bezpečnost": BRANCH_FI_MUNI_SEC,
        "Služby": BRANCH_FI_MUNI_SSME,
        "sítě a": BRANCH_FI_MUNI_PSK,
        "správě": BRANCH_FI_MUNI_INVS,
        "Paralelní": BRANCH_FI_MUNI_PDS,
        "Počítačové systémy": BRANCH_FI_MUNI_PSZD,
        "Programovatelné techni": BRANCH_FI_MUNI_PTS,
        "inteligence": BRANCH_FI_MUNI_UMI, 
        "Bio": BRANCH_FI_MUNI_BIO,
        "Soci": BRANCH_FI_MUNI_SOCI,
        "druhý": BRANCH_FI_MUNI_IO,
        "Kybernetická bezpečnost": BRANCH_FI_MUNI_KB,
        "Učitelství": BRANCH_FI_MUNI_UCI 
      }

  def get_others(self):     # get_thesis_list must be called first
    if not self.other_theses_retrieved:
      debug_print("WATCH OUT! calling get_others from FiMuniDownloader before get_thesis_list was called! Nothing will be returned.")
      return []

    return self.other_theses

  def get_thesis_list(self):
    def analyze_div(div, page_url):
      try:
        result = Thesis()
        result.city = CITY_BRNO
        result.faculty = FACULTY_FI_MUNI
        result.url_page = page_url
        result.public_university = True

        result.author = Person(div.find("b").string,False)

        if div.find("i",string="úspěšně absolvováno") != None:
          result.defended = True
        elif div.find("i",string="neúspěšně ukončen") != None:
          result.defended = False

        result.handle_branch(div.find_all("i")[4].string,self.substring_to_branch)
        
        title_string = div.find_all("i")[-1].string

        result.language = langdetect.detect(title_string) 

        if result.language not in (LANGUAGE_CS,LANGUAGE_SK,LANGUAGE_EN):
          result.language = None

        if result.language in (LANGUAGE_CS,LANGUAGE_SK):
          result.title_cs = title_string
        else:        
          result.title_en = title_string

        result.year = int(div.find("i",string="Fakulta informatiky").find_next("i").string)

        result.degree = div.find(lambda t: t.name == "i" and t.string in DEGREES).string

        result.kind = degree_to_thesis_type(result.degree)

        result.normalize()
        return result
      except Exception as e:
        debug_print("could not analyse thesis div: " + str(e))
        return None

    result = []

    soup = BeautifulSoup(download_webpage("https://is.muni.cz/thesis/?FAK=1433;PRI=-;ROK=-;TIT=-;PRA=-;vypsat=1;exppar=1;por=1"),"lxml")

    page_links = iterative_load(soup,
      lambda t: t.name == "nobr" and t.parent.name == "font",
      lambda t: FiMuniDownloader.BASE_URL + "thesis" + t.find_next("a")["href"][1:])

    # the list is doubled, as there are two link tables at the page (top and bottom) => take only the first half

    page_links = page_links[:len(page_links) / 2]

    for page in page_links:   # first page already loaded
      progress_print("downloading FI MUNI theses list for " + page)

      soup = BeautifulSoup(download_webpage(page),"lxml")

      result += iterative_load(soup,
        lambda t: t.name == "a" and t.string == "archiv",
        lambda t: FiMuniDownloader.BASE_URL[:-1] + t["href"])
 
      # retrieve other theses that don't have their own page:

      self.other_theses += iterative_load(soup,
        lambda t: t.name == "div" and t.parent.get("id") == "aplikace" and t.contents[0].name == "b" and t.find("a") == None,
        lambda t: analyze_div(t,page))

    self.other_theses_retrieved = True

    return result

  def get_thesis_info(self, url):
    result = Thesis()
    result.public_university = True

    result.faculty = FACULTY_FI_MUNI
    result.city = CITY_BRNO
    result.url_page = url

    soup = BeautifulSoup(download_webpage(url),"lxml") 

    current = soup.find(lambda t: t.get("id") == "metadata").find_next("b")

    result.author = Person(current.string)

    try:
      language_string = soup.find(lambda t: t.name == "p" and t.string != None and starts_with(t.string,"Jazyk práce:")).string[13:]

      if language_string == "angličtina":
        result.language = LANGUAGE_EN
      elif language_string == "čeština":
        result.language = LANGUAGE_CS
      elif language_string == "slovenština":
        result.language = LANGUAGE_SK
    except Exception as e:
      debug_print("could not resolve language:" + str(e))

    try:
      current = current.find_next("h2")

      if result.language in (LANGUAGE_CS,LANGUAGE_SK):
        result.title_cs = current.string
        next_sibling = current.find_next_sibling("h2")

        if next_sibling != None:
          result.title_en = next_sibling.string
      else:
        result.title_en = current.string
        next_sibling = current.find_next_sibling("h2")

        if next_sibling != None:
          result.title_cs = next_sibling.string
    except Exception as e:
      debug_print("could not resolve title: " + str(e))

    try:
      result.keywords = iterative_load(soup,
        lambda t: t.name == "span" and t.get("class") != None and t.get("class")[0] == "tg5",
        lambda t: t.contents[0].string)

      if len(result.keywords) > 0:
        if result.keywords[-1][-1] == ".":
          result.keywords[-1] = result.keywords[-1][:-1]

      result.field = guess_field_from_keywords(result.keywords)
    except Exception as e:
      debug_print("error at keywords/field: " + str(e))

    try:
      result.abstract_cs = soup.find("i",string="Anotace:").next_sibling.string.replace("\n"," ").rstrip().lstrip()
      result.abstract_en = soup.find("i",string="Abstract:").next_sibling.string.replace("\n"," ").rstrip().lstrip()
    except Exception as e:
      debug_print("could not resolve abstract:" + str(e))

    try:
      status_string = soup.find(lambda t: t.name == "h3" and t.string != None and starts_with(t.string,"Obhajoba")).string
      
      if status_string.find("bakalář") >= 0:
        result.kind = THESIS_BACHELOR
        result.degree = DEGREE_BC
      elif status_string.find("diplom") >= 0:
        result.kind = THESIS_MASTER
        result.degree = DEGREE_MGR
      elif status_string.find("disert") >= 0:
        result.kind = THESIS_PHD
        result.degree = DEGREE_PHD
      if status_string.find("rigor") >= 0:
        result.kind = THESIS_DR
        result.degree = DEGREE_RNDR
    except Exception as e:
      debug_print("could not resolve thesis kind: " + str(e))

    result.handle_branch(soup.find("h4",string="Masarykova univerzita").find_next("em").string,self.substring_to_branch)

    try:
      status_string = soup.find(lambda t: t.name == "h3" and t.string != None and starts_with(t.string,"Obhajoba")).find_next("li").contents[0]

      if status_string.find(" úspěš") >= 0:
        result.defended = True
    except Exception as e:
      debug_print("could not resolve defended state: " + str(e))

    try:
      fulltext_links = soup.find("h5",string="Plný text práce").find_next("ul").find_all(lambda t: t.name == "a" and t.find("img") == None) 
      fulltext_links = filter(lambda item: item.string.find("_pv_") == -1 and item.string.find("posudek") == -1,fulltext_links)
      result.url_fulltext = FiMuniDownloader.BASE_URL + fulltext_links[0]["href"]
    except Exception as e:
      debug_print("could not resolve fulltext: " + str(e))

    try:
      result.year = int(status_string.split(" ")[3][:-1])
    except Exception as e:
      debug_print("could not resolve year: " + str(e))

    try:
      supervisor_string = soup.find("h4",string="Vedoucí:").find_next("li").string
      result.supervisor = Person(supervisor_string)

      for department in DEPARTMENTS_MUNI:
        if supervisor_string.find(department) >= 0:
          result.department = department
          break

    except Exception as e:
      debug_print("could not resolve suprevisor: " + str(e))

    result.opponents = iterative_load(soup,
      lambda t: t.name == "li" and t.parent.find_previous_sibling(lambda t: t.name == "h4" and starts_with(t.string,"Oponent")) != None,
      lambda t: Person(t.string)
      )

    try:
      if result.url_fulltext[-4:].lower() == ".doc" or result.url_fulltext[-5:].lower() == ".docx":
        result.typesetting_system = SYSTEM_WORD
      elif result.url_fulltext[-4:].lower() == ".odt": 
        result.typesetting_system = SYSTEM_OPEN_OFFICE
      elif result.url_fulltext[-4:].lower() == ".pdf":
        pdf_info = download_and_analyze_pdf(result.url_fulltext)
        result.incorporate_pdf_info(pdf_info)
    except Exception as e:
      debug_print("could not analyze pdf: " + str(e))

    result.normalize()
    return result

#----------------------------------------

class PefMendeluDownloader(FacultyDownloader):

  BASE_URL = "https://is.mendelu.cz/zp/portal_zp.pl"

  def __init__(self):
    super(FacultyDownloader,self).__init__()
    self.name_to_year = {}

  def get_thesis_info(self,url):
    result = Thesis()
    result.url_page = url
    result.faculty = FACULTY_PEF_MENDELU
    result.public_university = True
    result.city = CITY_BRNO

    soup = BeautifulSoup(download_webpage(url,"ISO-8859-2"),"lxml")

    try:
      result.url_page = result.url_page[:result.url_page.find(";")]
    except Exception:
      pass

    def text_in_table(line):
      return soup.find("small",string=line).find_next("small").string

    try:
      type_string = text_in_table("Type of thesis: ")

      if type_string == "Bachelor thesis":
        result.kind = THESIS_BACHELOR
        result.degree = DEGREE_BC
      elif type_string == "Diploma thesis":
        result.kind = THESIS_MASTER
        result.degree = DEGREE_ING
      elif type_string == "Dissertation thesis":
        result.kind = THESIS_PHD
        result.degree = DEGREE_PHD
    except Exception as e:
      debug_print("could not resolve type/degree: " + str(e))

    try:
      result.author = Person(text_in_table("Written by (author): "))
      result.supervisor = Person(text_in_table("Thesis supervisor: "))

      if result.kind == THESIS_PHD: 
        result.opponents.append(Person(text_in_table("Opponent 1:")))
        result.opponents.append(Person(text_in_table("Opponent 2:")))
        result.opponents.append(Person(text_in_table("Opponent 3:")))
      else:
        result.opponents = [Person(text_in_table("Opponent:"))]

    except Exception as e:
      debug_print("could not resolve author/supervisor/opponent: " + str(e))

    try:
      defended_string = text_in_table("Final thesis progress:")

      if defended_string.find("was success") >= 0:
        result.defended = True
    except Exception as e:
      debug_print("could not resolve status: " + str(e))

    try:
      lang_string = text_in_table("Language of final thesis:")

      if lang_string == "Czech":
        result.language = LANGUAGE_CS
      elif lang_string == "English":
        result.language = LANGUAGE_EN
      elif lang_string == "Slovak":
        result.language = LANGUAGE_SK
    except Exception as e:
      debug_print("could not resolve language: " + str(e))

    try:
      # try to lead info in other language:

      if result.language == LANGUAGE_EN:
        url2 = url + "jazyk_zalozka=1;lang=cz"
      else:
        url2 = url + "jazyk_zalozka=3;lang=en"

      soup2 = BeautifulSoup(download_webpage(url2),"lxml")

      if result.language == LANGUAGE_EN:
        result.title_cs = soup2.find("small",string="Název práce:").find_next("small").string
        result.abstract_cs = soup2.find("small",string="Abstrakt:").find_next("small").string
      else:
        result.title_en = soup2.find("small",string="Title of the thesis:").find_next("small").string
        result.abstract_en = soup2.find("small",string="Summary:").find_next("small").string

    except Exception as e:
      debug_print("could not resolve other language info:" + str(e))

    try:
      title_string = text_in_table("Title of the thesis:")

      if title_string in self.name_to_year:
        result.year = self.name_to_year[title_string]

      abstract_string = text_in_table("Summary:")

      if result.language == LANGUAGE_EN:
        result.title_en = title_string
        result.abstract_en = abstract_string
      else:
        result.title_cs = title_string
        result.abstract_cs = abstract_string
    except Exception as e:
      debug_print("could not resolve title/abstract: " + str(e))

    try:
      result.keywords = beautify_list(text_in_table("Key words:").split(","))
      result.field = guess_field_from_keywords(result.keywords)
    except Exception as e:
      debug_print("could not resolve keywords: " + str(e))

    try:
      fulltext_string = soup.find("a",string="Final thesis")["href"]
      result.url_fulltext = PefMendeluDownloader.BASE_URL + fulltext_string[fulltext_string.find("?"):]
    except Exception as e:
      debug_print("could not resolve fulltext: " + str(e))

    try:
      pdf_info = download_and_analyze_pdf(result.url_fulltext)
      result.incorporate_pdf_info(pdf_info)
    except Exception as e:
      debug_print("could not analyze pdf: " + str(e))

    result.normalize()
    return result

  def get_thesis_list(self):
    result = []

    programs = (3,397,7,9,885,63)

    for program in programs:
      progress_print("downloading PF MENDELU thesis list, program " + str(program))

      param_string = "?razeni=fakulta;prehled=program;obor=0;forma=0;program=" + str(program) + ";obdobi=2013;obdobi=2014;obdobi=2015;obdobi=2016;obdobi=2017;obdobi=2018;dohledat=Dohledat;jazyk=1;jazyk=2;jazyk=3;lang=en"
      soup = BeautifulSoup(download_webpage(PefMendeluDownloader.BASE_URL + param_string),"lxml")

      temp_list = iterative_load(soup,
        lambda t: t.name == "a" and t.get("title") == "Displaying the final thesis",
        lambda t: (
          PefMendeluDownloader.BASE_URL + t["href"][t["href"].find("?"):],
          t.find_previous("small").find_previous("small").find_previous("small").find_previous("small").find_previous("small").string,
          int(t.find_previous("small").find_previous("small").find_previous("small").find_previous("small").string)
        ))

      for item in temp_list:
        self.name_to_year[item[1]] = item[2]

      result += map(lambda item: item[0],temp_list)

    return result

#----------------------------------------

class UcDownloader(FacultyDownloader):

  BASE_URL = "https://www.unicorncollege.cz/bakalarske-prace/"

  def get_thesis_info(self, url):
    result = Thesis()

    result.faculty = FACULTY_UC
    result.city = CITY_PRAHA
    result.public_university = False
    result.url_page = url
    result.kind = THESIS_BACHELOR
    result.degree = DEGREE_BC

    soup = BeautifulSoup(download_webpage(url),"lxml")

    def text_in_table(line):
      return soup.find("span",string=line).find_next("span").find_next("span").string

    try:
      result.author = Person(text_in_table("Autor"),False)
    except Exception as e:
      debug_print("could not resolve author: " + str(e)) 

    try:
      result.title_cs = text_in_table("Název")
    except Exception as e:
      debug_print("could not resolve title: " + str(e)) 

    try:
      result.year = int(text_in_table("Rok obhajoby"))
    except Exception as e:
      debug_print("could not resolve year: " + str(e)) 

    try:
      result.abstract_cs = text_in_table("Anotace")
    except Exception as e:
      debug_print("could not resolve abstract: " + str(e)) 

    try:
      relative_link = soup.find(lambda t: t.get("href") != None and t["href"][-4:].lower() == ".pdf")["href"]
      result.url_fulltext = url[:url.rfind("/") + 1] + relative_link
      pdf_info = download_and_analyze_pdf(result.url_fulltext)
      result.incorporate_pdf_info(pdf_info)
    except Exception as e:
      debug_print("could not download/analyze pdf: " + str(e)) 

    result.normalize()
    return result

  def get_thesis_list(self):
    result = []

    soup = BeautifulSoup(download_webpage(UcDownloader.BASE_URL + "bakalarske-prace.html"),"lxml")

    year_links = iterative_load(soup,
      lambda t: t.name == "span" and t.parent.name == "a" and t.parent.get("class")[0] == "uvcArtifact",
      lambda t: UcDownloader.BASE_URL + t.parent["href"])

    for year_link in year_links:
      progress_print("downloading UC link list for " + year_link)

      soup = BeautifulSoup(download_webpage(year_link),"lxml")

      links = iterative_load(soup,
        lambda t: t.name == "a" and t.get("class") != None and t.get("class")[0] == "uvcArtifact",
        lambda t: UcDownloader.BASE_URL + t["href"])

      result += links

    return result 

#----------------------------------------

if __name__ == "__main__":
  fit_but = FitButDownloader()
  ctu = CtuDownloader()
  ctu_extra = CtuExtraDownloader()
  fai_utb = FaiUtbDownloader()
  mff_cuni = MffCuniDownloader()
  fei_vsb = FeiVsbDownloader()
  fi_muni = FiMuniDownloader()
  pef_mendelu = PefMendeluDownloader()
  uc = UcDownloader()

  LINK_FILE_NAME = "links.txt"
  LINK_FILE_SHUFFLED = "links_shuffled.txt"
  DB_FILE = "theses.json"                    # final file to save the theses into
  OTHER_THESES_FILE = "other_theses.json"
  DONE_FILE = "already_done.txt"

  def make_thesis_list_file():    # makes a text file with all thesis URLs to be downloaded
    progress_print("------ making link file ------")

    link_list = []

    progress_print("-- downloading links for MFF CUNI")
    link_list += mff_cuni.get_thesis_list()

    progress_print("-- downloading links for FEI VSB")
    link_list += fei_vsb.get_thesis_list()

    progress_print("-- downloading links for PEF MENDELU")
    link_list += pef_mendelu.get_thesis_list()

    progress_print("-- downloading links for UC")
    link_list += uc.get_thesis_list()

    progress_print("-- downloading links for FAI UTB")
    link_list += fai_utb.get_thesis_list()

    progress_print("-- downloading links for CTU")
    link_list += ctu.get_thesis_list()

    progress_print("-- downloading links for CTU (extra)")
    link_list += ctu_extra.get_thesis_list()

    progress_print("-- downloading links for FIT BUT")
    link_list += fit_but.get_thesis_list()

    progress_print("-- downloading links for FI MUNI")
    link_list += fi_muni.get_thesis_list()

    link_file = open(LINK_FILE_NAME,"w")

    for link in link_list:
      link_file.write(link + "\n")

    link_file.close()

    progress_print("------- link file done -------")

  def shuffle_list_file():                 # shuffles the links so that the request rate on web servers is spread more evenly
    lines = get_file_text(LINK_FILE_NAME).split("\n")
    random.shuffle(lines)
    
    link_file_shuffled = open(LINK_FILE_SHUFFLED,"w")

    for line in lines:
      link_file_shuffled.write(line + "\n")

    link_file_shuffled.close()

  def download_theses(start_from=0, download_other=False):       # downloads all theses listed in the shuffled list file 
    #lines = get_file_text(LINK_FILE_SHUFFLED).split("\n")[start_from:]
    lines = get_file_text("links errors.txt").split("\n")[start_from:]

    if download_other:
      db_file = open(OTHER_THESES_FILE,"w")
      db_file.write("[\n")

      progress_print("downloading other theses from CTU")
      
      first = True

      for thesis in ctu.get_others():
        if first:
          first = False
        else:
          db_file.write(",\n")

        if thesis != None:
          db_file.write(str(thesis))
      
      progress_print("downloading other theses from FI MUNI")
      fi_muni.get_thesis_list()   # has to be done

      for thesis in fi_muni.get_others():
        db_file.write(",\n")

        if thesis != None:
          db_file.write(str(thesis))

      db_file.write("\n]\n")
      db_file.close()
      return

    # normal download:

    counter = 0

    #if start_from == 0:
    db_file = open(DB_FILE,"w")
    #db_file.write("[\n")
    #else:
    #db_file = open(DB_FILE,"a")

    first = True
    big_errors = 0
    failed_links = []
   
    for line in lines:
      progress_print("downloading thesis " + str(counter) + "/" + str(len(lines)) + ", url: " + line)
  
      for i in range(5):  # try 5 times  
        try: 
          append_string = None

          if line.find("fit.vutbr.") >= 0:
            progress_print("FIT BUT")
            thesis = fit_but.get_thesis_info(line) 
            append_string = str(thesis) if thesis != None else None
          elif line.find("is.muni.cz") >= 0:
            progress_print("FI MUNI")
            thesis = fi_muni.get_thesis_info(line)
            append_string = str(thesis) if thesis != None else None
          elif line.find("felk.cvut") >= 0:
            progress_print("CTU")
            thesis = ctu.get_thesis_info(line)
            append_string = str(thesis) if thesis != None else None
          elif line.find("dspace.cvut") >= 0:
            progress_print("CTU2")
            thesis = ctu_extra.get_thesis_info(line)
            append_string = str(thesis) if thesis != None else None
          elif line.find("dspace.vsb") >= 0:
            progress_print("VSB")
            thesis = fei_vsb.get_thesis_info(line)
            append_string = str(thesis) if thesis != None else None
          elif line.find("is.cuni") >= 0:
            progress_print("MFF CUNI")
            thesis = mff_cuni.get_thesis_info(line)
            append_string = str(thesis) if thesis != None else None
          elif line.find(".utb.") >= 0:
            progress_print("FAI UTB")
            thesis = fai_utb.get_thesis_info(line)
            append_string = str(thesis) if thesis != None else None
          elif line.find("portal_zp.pl") >= 0:
            progress_print("PEF MENDELU")
            thesis = pef_mendelu.get_thesis_info(line)
            append_string = str(thesis) if thesis != None else None
          elif line.find(".unicorncollege.") >= 0:
            progress_print("UC")
            thesis = uc.get_thesis_info(line)
            append_string = str(thesis) if thesis != None else None
          else:
            progress_print("unknown link!!!: " + line.replace("\n",""))

          if append_string != None:
            if first:
              first = False
            else:
              db_file.write(",\n")

            db_file.write(append_string)

          counter += 1
          break
        except Exception as e:
          progress_print("BIG ERROR: " + str(e))
          traceback.print_exc(file=sys.stdout)
          big_errors += 1
          progress_print("there were " + str(big_errors) + " big errors so far")

          if i < 4:
            progress_print("trying again...")
          else:
            progress_print("abandoning, there are " + str(len(failed_links)) + " failed links so far")
            failed_links.append(line)

        progress_print("failed links so far: " + str(failed_links))

    #db_file.write("\n]\n")
    db_file.close()

  #======================

  #make_thesis_list_file()
  #shuffle_list_file()
  download_theses()
  #print(PDFInfo("test_smrcka.pdf").typesetting_system)
  #download_theses()

  #print(mff_cuni.get_thesis_info("https://is.cuni.cz/webapps/zzp/detail/49648/25061566/?q=%7B%22______searchform___search%22%3A%22%22%2C%22______searchform___butsearch%22%3A%22Vyhledat%22%2C%22______facetform___facets___faculty%22%3A%5B%2211320%22%5D%2C%22PNzzpSearchListbasic%22%3A%22158%22%7D&lang=cs"))
  #print(fi_muni.get_thesis_info("https://is.muni.cz/th/359420/fi_b/"))
  #print(fit_but.get_thesis_info("http://www.fit.vutbr.cz/study/DP/DP.php?id=19244&y=2016"))
  #print(ctu.get_thesis_info("https://dip.felk.cvut.cz/browse/details.php?f=F3&d=K13136&y=2007&a=bilekj2&t=dipl")  )
  #print(pef_mendelu.get_thesis_info("https://is.mendelu.cz/zp/portal_zp.pl?podrobnosti_zp=56535"))

#  print(download_webpage("http://is.muni.cz/thesis/"))
#  print( BeautifulSoup(download_webpage("http://torguard.net/whats-my-ip.php"),"lxml").find("strong").find_next("strong").next_sibling   )


