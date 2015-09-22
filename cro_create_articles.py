import codecs
import re
import sys
import json
import os
import random


def get_article_id(line):
    print line
    id = re.search(r'"[0-9]*"', line).group()
    return id[1:len(id) - 1]

def cro_create_articles(fileIn, dirOut):
    with codecs.open(fileIn, 'r', encoding='utf8') as fIn:
        flag = 0
        counter = 0
        content = ""
        for line in fIn:
            if "<articlePair" in line:
                article_id = get_article_id(line)
            if "<content>" in line and flag == 0:
                flag = 1
            elif "</content>" in line and flag == 1:
                flag = 2
            elif "<content>" in line and flag == 2:
                flag = 3    
            elif "</content>" in line and flag == 3:
                fileOut = dirOut + "/" + str(article_id) + ".txt"
                with codecs.open(fileOut, 'w', encoding='utf8') as fOut:
                    fOut.write(content)
                                 
                counter += 1
                flag = 0
                content = ""              
                  
            elif flag == 1:
                content += " " + line
                
        print "Wrote " + str(counter) + " files in '" + dirOut + "'"
    
        
if __name__ == '__main__':
    fileIn = "Data/hren/wikicomp-2015_hren.xml"
    dirOut = "Data/hren/hren_articles/"
    print cro_create_articles(fileIn, dirOut)
