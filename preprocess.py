#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import multiprocessing
import sys
from bs4 import BeautifulSoup
import codecs
import getopt
import json
from nltk.tokenize import word_tokenize
import os
import random
import re
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

class PreprocessWorker(object):
    noun = {"en":"NN", "de":"NN", "it":"NOM", "es":"NC", "fr":"NOM"}
    langs = {"en":"english", "de":"german", "it":"italian", "es":"spanish", "fr":"french"}
    
    def __init__(self, directory, fileIn, n, numProcs, randomShuffle):
        
        self.directory = directory
        self.fileIn = fileIn
        self.n = n
        self.numProcs = numProcs
        self.randomShuffle = randomShuffle
        self.inq = multiprocessing.Queue()
        self.outq = multiprocessing.Queue()
        
        manager = multiprocessing.Manager()
        self.dict1 = manager.dict()
        self.dict2 = manager.dict()

        self.pin = multiprocessing.Process(target=self.parse_input, args=())
        self.pout = multiprocessing.Process(target=self.write_output, args=())
        self.ps = [ multiprocessing.Process(target=self.process, args=())
                        for i in range(self.numProcs) ]

        with codecs.open(self.fileIn, 'r', encoding='utf8') as fIn:
            langs = fIn.readline()
            while not re.search("<wikipediaComparable name=", langs):
                langs = fIn.readline()
            
            self.setOutputFilenames(langs)

        self.pin.start()
        self.pout.start()
        for p in self.ps:
            p.start()

        self.pin.join()
        i = 0
        for p in self.ps:
            p.join()
            print "Done", i
            i += 1

        self.pout.join()
        
    def setOutputFilenames(self, line):
        l1 = re.search(r'"[A-Za-z-]*-', line).group()
        l2 = re.search(r'-[A-Za-z]*"', line).group()
        lan1 = l1[1:len(l1) - 1]
        lan2 = l2[1:len(l2) - 1]
                 
        self.pseudoFileOut = self.directory + "text_" + lan1 + lan2 + ".txt"
        self.dictFile1 = self.directory + "dict_" + lan1 + ".txt"
        self.dictFile2 = self.directory + "dict_" + lan2 + ".txt"
        self.lanFile1 = self.directory + "text_" + lan1 + ".txt"
        self.lanFile2 = self.directory + "text_" + lan2 + ".txt"
        self.lan1 = lan1
        self.lan2 = lan2
        
    def removeHtml(self, content):
        soup = BeautifulSoup(content)
        return soup.getText()
    
    def tokenize(self, content):
        tokens = word_tokenize(content)
        for i in xrange(len(tokens)):
            tokens[i] = re.sub(ur"[^A-Za-z'-]+", "", tokens[i], re.UNICODE)
        return [ re.sub(ur"\W\W", "", token, re.UNICODE) for token in tokens if len(token) > 1]
    
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
    
    def getCroatianTokens(self, id):
        fileIn = "Data/" + self.lan1 + self.lan2 + "/hr_articles_preprocessed/" + str(id) + ".txt"
        
        if not os.path.exists(fileIn):
            return []
        
        tokens = list()
        with codecs.open(fileIn, 'r', encoding='utf8') as fIn:  
            for line in fIn:   
                items = line.split('\t')
                if len(items) > 2 and len(items[2]) > 1 and not items[2][0].isdigit() and items[4] == "N":
                    tokens.append(items[2])
        return tokens
    
    def getArticleId(self, line):
        id = re.search(r'"[0-9]*"', line).group()
        return id[1:len(id) - 1]

    def parse_input(self):
        """
        Parse the input Wikipedia Comparable xml file and yield tuples with the index
        of the article pair as the first element, and the list containing article
        contents as the second element.
        
        Index is zero-based.
        
        The data is then sent over inqueue for the workers to do preprocessing of each
        article pair.  At the end the input process send a 'STOP' message for each
        worker.
        """
        with codecs.open(self.fileIn, 'r', encoding='utf8') as fIn:
            flag = 0
            counter = 0
            content1 = ""
            content2 = ""
            articleId = -1
            for line in fIn:
                if "<articlePair" in line:
                    articleId = self.getArticleId(line)                
                elif "<content>" in line and flag == 0:
                    flag = 1
                elif "</content>" in line and flag == 1:
                    flag = 2
                elif "<content>" in line and flag == 2:
                    flag = 3    
                elif "</content>" in line and flag == 3:        
                    articlePair = [ content1, content2, articleId ]
                    self.inq.put((counter, articlePair))
                    
                    counter += 1
                    content1 = ""
                    content2 = ""
                    flag = 0
                    
                    if counter >= self.n and self.n > 0:
                        break
                    
                    if counter % 100 == 0:
                        print counter
                    
                elif flag == 1:
                    content1 += " " + line
                elif flag == 3:
                    content2 += " " + line
        
            for i in range(self.numProcs):
                self.inq.put("STOP")

    def process(self):
        """
        Workers.
                
        - Consume article pairs from inq and produce shuffled pairs on outq     
            - Shuffled pairs are made of lemmatized forms of nouns
        - Produce processed language files for testing Mikolov model
        - Work on creating dictionaries
        - Send STOP signal through outq when no more work to be done
        """
        
        if self.lan1 != "hr":
            tt1 = TreeTagger(encoding='utf8', language=PreprocessWorker.langs[self.lan1])
            
        if self.lan2 != "hr":
            tt2 = TreeTagger(encoding='utf8', language=PreprocessWorker.langs[self.lan2])
        
        for i, article in iter(self.inq.get, "STOP"):
            content1 = article[0]
            content2 = article[1]
            articleId = article[2]
                        
            if self.lan1 == "hr":
                tokens1 = self.getCroatianTokens(articleId)  
                if len(tokens1) < 10:
                    continue              
            else:
                tokens1 = self.tokenize(self.removeHtml(content1.lower()))    
                if len(tokens1) < 10:
                    continue   
                tokens1 = tt1.tag(tokens1)
                tokens1 = [lemma.lower() if lemma != '<unknown>' else token.lower() for token, tag, lemma in tokens1 if tag == PreprocessWorker.noun[self.lan1]]
            
            if self.lan2 == "hr":
                tokens2 = self.getCroatianTokens(articleId)
                if len(tokens2) < 10:
                    continue
            else: 
                tokens2 = self.tokenize(self.removeHtml(content2.lower()))
                if len(tokens2) < 10:
                    continue
                tokens2 = tt2.tag(tokens2)
                tokens2 = [lemma.lower() if lemma != '<unknown>' else token.lower() for token, tag, lemma in tokens2 if tag == PreprocessWorker.noun[self.lan2]]
            
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
                        
            article1 = ' '.join(tokens1) + " "
            article2 = ' '.join(tokens2) + " "
            self.outq.put((i, articlePair, article1, article2))  
                        
        self.outq.put("STOP")
        
    def write_output(self):
        """
        - Read outq for processed article pairs and separate articles
        - Output prepared articles and separate articles to files until 
        all STOP signals are received from preprocessing processes  
        - Output dictionaries              
        """
        pseudoFOut = codecs.open(self.pseudoFileOut, 'w', encoding='utf-8')
        lanFOut1 = codecs.open(self.lanFile1, 'w', encoding='utf-8')
        lanFOut2 = codecs.open(self.lanFile2, 'w', encoding='utf-8')        
        
        # Keep running until receiving numProcs STOP messages
        for works in range(self.numProcs):
            for i, articlePair, article1, article2 in iter(self.outq.get, "STOP"):
                # The order of articles is not relevant at this point so just output processed article pair
                pseudoFOut.write(articlePair + "\n")                
                lanFOut1.write(article1 + "\n")
                lanFOut2.write(article2 + "\n")
        
        pseudoFOut.close()
        lanFOut1.close()
        lanFOut2.close()
        
        json.dump(self.dict1.copy(), codecs.open(self.dictFile1, 'w', encoding='utf-8'), ensure_ascii=False)
        json.dump(self.dict2.copy(), codecs.open(self.dictFile2, 'w', encoding='utf-8'), ensure_ascii=False)
                

def preprocess(directory, fileIn, n, numProcs, randomShuffle):
    pw = PreprocessWorker(directory, fileIn, n, numProcs, randomShuffle)

def main(sys_argv):
    try:
        opts, argv = getopt.getopt(sys_argv[1:], 'd:n:rh', ["directory=", "num=", "random", "help"])
    except getopt.GetoptError, err:
        print str(err)
        usage()
        sys.exit(1)
        
    outputDir = ""
    fileIn = None
    n = 0
    random = False
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
                
    numProcs = multiprocessing.cpu_count()
    preprocess(outputDir, fileIn, n, numProcs, random)

if __name__ == '__main__':
    main(sys.argv)
