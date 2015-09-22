# -*- coding: utf-8 -*-

import csv
import codecs
from os import listdir
from os import remove
from os.path import isfile, join


path = "Data/hren/hr_articles_preprocessed/"

files = [ join(path,f) for f in listdir(path) if isfile(join(path,f)) ]

# # Remove empty lines from files
# for fileIn in files:
#     with codecs.open(fileIn, 'r', encoding='utf8') as fIn: 
#         fileOut = fileIn + ".stripped"
#         fOut = codecs.open(fileOut, 'w', encoding='utf8')
#         for line in fIn:
#             if len(line) < 4:
#                 continue
#             else:
#                 fOut.write(line + "\n")
#     remove(fileIn)

def getCroatianTokens(id):
    fileIn = "Data/hren/hr_articles_preprocessed/" + str(id) + ".txt"
    
    tokens = list()
    with codecs.open(fileIn, 'r', encoding='utf8') as fIn:  
        for line in fIn:   
            items = line.split('\t')
            if len(items) > 2 and len(items[2]) > 1 and not items[2][0].isdigit() and items[4] == "N":
                tokens.append(items[2])
    return tokens

tokens = getCroatianTokens(2)
print tokens[1]



# 
# for fileIn in files:
#     with codecs.open(fileIn, 'r', encoding='utf8') as fIn:  
#         for line in fIn:   
#             items = line.split('\t')
#             if len(items) > 2 and len(items[2]) > 1 and not items[2][0].isdigit() and items[4] == "N":
#                 print items[2] + " " + items[4]
#             