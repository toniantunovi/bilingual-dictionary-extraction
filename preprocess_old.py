# coding: utf-8

from bs4 import BeautifulSoup
import codecs
import getopt
import json
from nltk.tokenize import word_tokenize
import os
import random
import re
import sys
from treetagger import TreeTagger


def usage(errno=0):
    print >> sys.stderr, \
    """
    Given a XML file from The Wikipedia Comparable Corpora 
    (http://linguatools.org/tools/corpora/wikipedia-comparable-corpora/) create
    pseudodocument (Vulic, 2015) and documents for two languages ready to be trained using word2vec (Mikolov, 2013).
    Output dictionaries for both languages in json, all based on first N articles in source file. 
    
    Usage:
    python preprocess.py [options] wikipedia_comp_corp_file lan1 lan2 
    \n\
    Options:
    -d --directory <directory>: output directory. Default is current directory
    -n --num <int>: Number of articles from source file to be used. Default is all articles     
    -r --random: Use random shuffling for creation of pseudodocument                     
    -h --help : help

    Arguments:
    file: <file>, The Wikipedia Comparable Corpora file

    Examples:
    1) Tokenize first 10000 documents from Data/wikicomp-2014_deit.xml file and create output in Data folder
    
    python preprocess.py -n 10000 -d Data/deit/output/ Data/wikicomp-2014_deit.xml
    
    
    2) Tokenize all documents from Data/wikicomp-2014_deit.xml file and create output in Data folder

    python preprocess.py -d Data/deit/output/ Data/wikicomp-2014_deit.xml

    """
    sys.exit(errno)

class Preprocessor():
    noun = {"en":"NN", "de":"NN", "it":"NOM", "es":"NC"}
    langs = {"en":"english", "de":"german", "it":"italian", "es":"spanish"}
    
    def __init__(self, directory, fileIn, n, randomShuffle):
        
        self.fileIn = fileIn
        self.directory = directory + "/"
        self.randomShuffle = randomShuffle
        self.n = n
        self.flag = 0
        self.counter = 0        
        self.content1 = ""
        self.content2 = ""
        self.dict1 = dict()
        self.dict2 = dict()
        if not os.path.exists(directory):
            os.makedirs(directory)
        
    def setOutputFilenames(self, line):
        l1 = re.search(r'"[A-Za-z-]*-', line).group()
        l2 = re.search(r'-[A-Za-z]*"', line).group()
        lan1 = l1[1:len(l1) - 1]
        lan2 = l2[1:len(l2) - 1]
        
        print "Lan1 = " + lan1
        print "Lan2 = " + lan2
         
        self.pseudoFileOut = self.directory + "text_" + lan1 + lan2 + ".txt"
        self.dictFile1 = self.directory + "dict_" + lan1 + ".txt"
        self.dictFile2 = self.directory + "dict_" + lan2 + ".txt"
        self.lanFile1 = self.directory + "text_" + lan1 + ".txt"
        self.lanFile2 = self.directory + "text_" + lan2 + ".txt"
        self.lan1 = lan1
        self.lan2 = lan2
        
    def getArticleWithRandomShuffle(self, tokens1, tokens2):
        return ' '.join(random.sample(tokens1 + tokens2, len(tokens1) + len(tokens2))) + " "
    
    def getArticleWithSmartShuffle(self, tokens1, tokens2, ratio):
        article = ""
        num = 0
        for token in tokens2:
            for i in xrange(ratio):
                article += tokens1[num + i] + " "
            article += token + " "
            num += i + 1
        
        return article + ' '.join(tokens1[num:]) + " "
        
    def Process(self):
        
        print "Preprocessing started..."        
        with codecs.open(self.fileIn, 'r', encoding='utf8') as fIn:            
            
            langs = fIn.readline()
            while not re.search("<wikipediaComparable name=", langs):
                langs=fIn.readline()
            
            self.setOutputFilenames(langs)
            pseudoFOut = codecs.open(self.pseudoFileOut, 'w', encoding='utf-8')
            lanFOut1 = codecs.open(self.lanFile1, 'w', encoding='utf-8')
            lanFOut2 = codecs.open(self.lanFile2, 'w', encoding='utf-8')
            tt1 = TreeTagger(encoding='utf8', language=Preprocessor.langs[self.lan1])
            tt2 = TreeTagger(encoding='utf8', language=Preprocessor.langs[self.lan2])
                        
            for line in fIn:
                if "<content>" in line and self.flag == 0:
                    self.flag = 1
                elif "</content>" in line and self.flag == 1:
                    self.flag = 2
                elif "<content>" in line and self.flag == 2:
                    self.flag = 3    
                elif "</content>" in line and self.flag == 3:                                                         
                    tokens1 = self.tokenize(self.removeHtml(self.content1.lower()))       
                    tokens1 = tt1.tag(tokens1)
                    tokens1 = [lemma.lower() if lemma != '<unknown>' else token.lower() for token, tag, lemma in tokens1 if tag == Preprocessor.noun[self.lan1]]
                                        
                    tokens2 = self.tokenize(self.removeHtml(self.content2.lower()))
                    tokens2 = tt2.tag(tokens2)                                   
                    tokens2 = [lemma.lower() if lemma != '<unknown>' else token.lower() for token, tag, lemma in tokens2 if tag == Preprocessor.noun[self.lan2]]
                    
                    for i in xrange(len(tokens1)):
                        if self.dict1.has_key(tokens1[i]):
                            self.dict1[tokens1[i]] += 1
                        else:
                            self.dict1[tokens1[i]] = 1
                            
                    for i in xrange(len(tokens2)):
                        if self.dict2.has_key(tokens2[i]):
                            self.dict2[tokens2[i]] += 1
                        else:
                            self.dict2[tokens2[i]] = 1
                    
                    if len(tokens1) < 2 or len(tokens2) < 2:
                        continue
                    
                    if self.randomShuffle:
                        articlePair = self.getArticleWithRandomShuffle(tokens1, tokens2)                 
                    else:                        
                        if len(tokens1) > len(tokens2):                    
                            ratio = len(tokens1) / len(tokens2)
                            articlePair = self.getArticleWithSmartShuffle(tokens1, tokens2, ratio)                    
                        else:
                            ratio = len(tokens2) / len(tokens1)
                            articlePair = self.getArticleWithSmartShuffle(tokens2, tokens1, ratio)     
                                                         
                    pseudoFOut.write(articlePair + "\n")                      
                    lanFOut1.write(' '.join(tokens1) + "\n")
                    lanFOut2.write(' '.join(tokens2) + "\n")                  
                    
                    self.content1 = ""
                    self.content2 = ""
                    self.flag = 0
                    self.counter += 1
                    if self.counter >= self.n and self.n > 0:
                        break
                    
                    if self.counter % 100 == 0:
                        print self.counter
                    
                elif self.flag == 1:
                    self.content1 += " " + line
                elif self.flag == 3:
                    self.content2 += " " + line
        
        json.dump(self.dict1, codecs.open(self.dictFile1, 'w', encoding='utf-8'), ensure_ascii=False)
        json.dump(self.dict2, codecs.open(self.dictFile2, 'w', encoding='utf-8'), ensure_ascii=False)
        
        fIn.close()
        pseudoFOut.close()
        lanFOut1.close()
        lanFOut2.close()        
        
        print "Preprocessing done."
        print "Nouns in " + self.dictFile1 + ": " + str(len(self.dict1))
        print "Nouns in " + self.dictFile2 + ": " + str(len(self.dict2))
        
    def removeHtml(self, content):
        soup = BeautifulSoup(content)
        return soup.getText()
    
    def tokenize(self, content):
        tokens = word_tokenize(content)
        for i in xrange(len(tokens)):
            tokens[i] = re.sub(ur"[^A-Za-z'-]+", "", tokens[i], re.UNICODE)
        return [ re.sub(ur"\W\W", "", token, re.UNICODE) for token in tokens if len(token) > 1]


def preprocess(directory, fileIn, n, random):
    pp = Preprocessor(directory, fileIn, n, random)
    pp.Process()


def main(sys_argv):
    try:
        opts, argv = getopt.getopt(sys_argv[1:], 'd:n:rh', ["directory=", "num=", "random", "help"])
    except getopt.GetoptError, err:
        print str(err)
        usage()
        sys.exit(1)
        
    outputDir = ""
    fileIn = None
    random = False
    n = 0
    for opt, val in opts:
        if opt in ("-d", "--directory"):
            outputDir = val
        elif opt in ("-n", "--num"):
            try:
                n = int(val)
            except ValueError:
                usage(1)                
        elif opt in ("-r", "--random"):
            random = True
        elif opt in ("-h", "--help"):
            usage(0)
        else:
            usage(1)
    
    if len(argv) == 1:
        fileIn = argv[0]
    else:
        usage(1)
        
    preprocess(outputDir, fileIn, n, random)
        
    
if (__name__ == "__main__"):
    main(sys.argv)
    
