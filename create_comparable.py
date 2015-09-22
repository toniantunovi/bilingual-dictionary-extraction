#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import multiprocessing
import codecs
import getopt
import requests
import sys
from bs4 import BeautifulSoup

def usage(errno=0):
    print >> sys.stderr, \
    """
    Create Wikipedia comparable corpora taking only index of source language Wikipedia
    Output to file in Wikipedia Comparable xml format 
    (http://linguatools.org/tools/corpora/wikipedia-comparable-corpora/)
   
    Usage:
    python create_comparable.py <options> lan1 lan2 outputFile
    python test_full.py --help
    
    Options:
    -h --help: help
    -n --num: number of articles
    
    Arguments:
    lan1, lan2: language codes (en - english, de - german, es - spanish, fr - french, it - italian, hr - croatian)
    outputFile: Wikipedia Comparable Output file     
        
    Examples:
    1) Create croatian-english comparable corpora with 200 comparable articles   
    python create_comparable.py -n 100000 Data/enhr/hrwiki-20150316-pages-articles-multistream-index.txt hr en Data/enhr/wikicomp-2015_100000_hren.xml
       
    2) Show help:
    python create_comparable.py --help    
    """
    sys.exit(errno)

class CreateComparableWorker(object):    
    def __init__(self, lan1IndexFile, lan1, lan2, outputFile, numProcs, n):
        
        self.lan1IndexFile = lan1IndexFile
        self.lan1 = lan1
        self.lan2 = lan2
        self.outputFile = outputFile
        self.numProcs = numProcs
        self.n = n
        
        self.inq = multiprocessing.Queue()
        self.outq = multiprocessing.Queue()
       
        self.pin = multiprocessing.Process(target=self.parse_input, args=())
        self.pout = multiprocessing.Process(target=self.write_output, args=())
        self.ps = [ multiprocessing.Process(target=self.process, args=())
                        for i in range(self.numProcs) ]

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
    
    
    def parse_input(self):
        counter = 0
        fIn = codecs.open(self.lan1IndexFile, 'r', encoding='utf8')
        
        for line in fIn:
            lline = line.lower()
            if 'wiki' in lline or '.jpg' in lline:
                continue
            
            source = line[line.rfind(':')+1:len(line)-1].replace(" ", "_")        
            url = "http://www.wikidata.org/w/api.php?action=wbgetentities&sites=" + self.lan1 + "wiki&titles=" + source + "&languages=" + self.lan2 + "&props=labels&format=json"
            r = requests.get(url);
            
            try:
                index, = r.json().values()[0]
                res_type = r.json().values()[0].values()[0].values()[0]            
                if index != '-1' and res_type != 'item':                
                    counter += 1
                    target = r.json()['entities'].values()[0]['labels'][self.lan2]['value'].replace(" ", "_")
                    self.inq.put((counter, source, target))
                    
                    if self.n is not None and counter == self.n:
                        break
                
                    if counter % 100 == 0:
                        print counter
            except:
                print "Error in response format! Skipping current article and continuing..."
                
             
        fIn.close()
        for i in range(self.numProcs):
            self.inq.put("STOP")
        
    def process(self):
        for id, source, target in iter(self.inq.get, "STOP"):        
            url1 = "http://" + self.lan1 + ".wikipedia.org/w/api.php?action=parse&page=" + source + "&format=xml"
            r1 = requests.get(url1)
            html1 = BeautifulSoup(r1.text).api.parse
            if not html1:
                continue
            else:
                html1 = html1.text            
            article1 = ' '.join([ p.getText() for p in BeautifulSoup(html1).findAll("p")])
                      
            url2 = "http://" + self.lan2 + ".wikipedia.org/w/api.php?action=parse&page=" + target + "&format=xml"
            r2 = requests.get(url2)                        
            html2 = BeautifulSoup(r2.text).api.parse
            if not html2:
                continue
            else:
                html2 = html2.text
            article2 = ' '.join([ p.getText() for p in BeautifulSoup(html2).findAll("p")])
            
            articlePairOutput = "<articlePair id=\"" + str(id) + "\">\n"
            articlePairOutput += "<article lang=\"" + self.lan1 + "\" name=\"" + source.replace("_"," ") + "\">\n"
            articlePairOutput += "<categories name=\"\"/>\n"
            articlePairOutput += "<content>\n" + article1 + "\n</content>\n</article>\n"
            
            articlePairOutput += "<article lang=\"" + self.lan2 + "\" name=\"" + target.replace("_"," ") + "\">\n"
            articlePairOutput += "<categories name=\"\"/>\n"
            articlePairOutput += "<content>\n" + article2 + "\n</content>\n</article>\n"
            
            articlePairOutput += "</articlePair>\n"
            
            self.outq.put(articlePairOutput)
                        
        self.outq.put("STOP")
        
    def write_output(self):        
        fOut = codecs.open(self.outputFile, 'w', encoding='utf8')    
        fOut.write("<wikipediaComparable name=\"" + self.lan1 + "-" + self.lan2 + "\">\n<header>\n</header>\n")
        
        for works in range(self.numProcs):
            for articlePair in iter(self.outq.get, "STOP"):                
                fOut.write(articlePair + "\n")
        
        fOut.write("</wikipediaComparable>")
        fOut.close()
                

def create_comparable(lan1IndexFile, lan1, lan2, outputFile, numProcs, n):
    CreateComparableWorker(lan1IndexFile, lan1, lan2, outputFile, numProcs, n)

def main(sys_argv):        
    try:
        opts, argv = getopt.getopt(sys_argv[1:], 'n:', ["num="])
    except getopt.GetoptError, err:
        print str(err)
        usage()
        sys.exit(1)
    
    n = None
    for opt, val in opts:
        if opt in ("-n", "--num"):
            try:
                n = int(val)
            except ValueError:
                usage(1)        
        else:
            usage(1)
        
    if len(argv) == 4:
        lan1IndexFile = argv[0]
        lan1 = argv[1]
        lan2 = argv[2]
        outputFile = argv[3]
    else:
        usage(1)
                
    numProcs = multiprocessing.cpu_count()
    create_comparable(lan1IndexFile, lan1, lan2, outputFile, numProcs, n)

if __name__ == '__main__':
    main(sys.argv)
