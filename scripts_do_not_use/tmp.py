#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

sys.path.insert(0,"../tools")

import theses_common

theses = theses_common.load_json("theses_sexes.json")

weird_male_names = ["Ľuboš","Róbert","Valter","Bronislav","Mário","Leopold","Bohumír","Ervín","Mirón","Kiryl","Vitalii","Andrii","Ievgen","Tarek","Maroš","Ferdinand","Sebastián","Denis","Adrián","Abdullah","István","Hristo","Břetislav","Giuseppe","Oliver","Valentyn","Valentin","Adrian","Denis","Blažej","Konrád","Prokop","Oleksandr","Mikhail","Agron","Norbert","Jean","Janusz","Sergey","Imrich","Nikolaj","András","Sultan","Riva","Susil","Yuriy","José","Radko","Dilip","Nikolas","Sergeii","Silvester","Vladyslav","Albert","Anton","Ahmad","Krzysztof","Julius","Frederik","Alexei","Tom","Jasmin","Andrey","Walter","Jorge","Gábor","Severin","Mirko","Aliaksandr","Benjam"]
weird_female_names = ["Olha","Mariia","Ilana","Arina","Tanya","Jonathan","Khrystyna","Irina","Zuena","Feraena","Dinara","Maria","Elena","Sara","Marharyta","Yelena","Natalya","Svetlana"]

for thesis in theses:
  if thesis["author"] != None and thesis["author"]["sex"] == None:
    #print(thesis["author"])

    p = theses_common.Person(thesis["author"]["name_last"] + " " + thesis["author"]["name_first"])

    if p.sex != None:
      print(thesis["author"]["name_first"] + " " + thesis["author"]["name_last"] + ": " + p.sex)

      thesis["author"]["name_first"] = thesis["author"]["name_last"]
      thesis["author"]["name_last"] = p.name_first
      thesis["author"]["sex"] = p.sex

    #if thesis["author"]["name_first"] in weird_male_names:
    #  thesis["author"]["sex"] = "male"
    #  print("setting to male")
    #elif thesis["author"]["name_first"] in weird_female_names:
    #  thesis["author"]["sex"] = "female"
    #  print("setting to female")

theses_common.save_json(theses,"theses_sexes.json") 
