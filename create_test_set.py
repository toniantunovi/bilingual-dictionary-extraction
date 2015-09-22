# coding: utf-8

import codecs
import goslate
import getopt
import json
import random
import sys
import operator
from space import Space
from preprocess import PreprocessWorker
from treetagger import TreeTagger

def usage(errno=0):
    print >> sys.stderr, \
    """
    Create test set
    
    Take the source dictionary and sort it in descending order. Find 3*n translation pairs.
    Randomly sample n pairs from 3*n previously extracted pairs.
    
    Usage:
    python create_test_set.py directory lan1 lan2 n
    python create_test_set.py --help
    
    Options:
    -h --help: help
    
    Arguments:
    directory: path to the directory containing preprocessing and word2vec output files
    lan1, lan2: language codes (en - english, de - german, es - spanish, fr - french, it - italian, hr - croatian)
    n: number of word pairs in test set
        
    Examples:
    1) Create test set containing 1000 word pairs for deen corpora 
    python create_test_set.py Data/deen/output/ en de 1000
    
    2) Show help:
    python create_test_set.py --help
    """
    sys.exit(errno)


def create_dict(directory, lan1, lan2, num):
    dictFile1 = directory + "/dict_" + lan1 + ".txt"
    dictFile2 = directory + "/dict_" + lan2 + ".txt"
    dictFileOutput = directory + "/dict_" + lan1 + lan2 + ".txt"
    word2vecFile = directory + "/vec_" + lan1 + lan2 + ".txt"

    print "Loading dictionaries..."
    gs = goslate.Goslate()
    dict1 = json.load(codecs.open(dictFile1, 'r', encoding='utf8'))
    dict2 = json.load(codecs.open(dictFile2, 'r', encoding='utf8'))
    dictOutput = dict()
    
    source_words = set(dict1.keys())
    sp1 = Space.build(word2vecFile, source_words)
    target_words = set(dict2.keys())
    sp2 = Space.build(word2vecFile, target_words)
    
    print "Sorting source language dictionary..."    
    items = sorted(dict1.items(), key=operator.itemgetter(1), reverse=True)    
    
#     tt = TreeTagger(encoding='utf8', language=PreprocessWorker.langs[lan2])
    
    print "Translating..."    
    counter = 0    
    for key, value in items:
        translation = gs.translate(key, lan2, lan1)
#         tokens = tt.tag(translation)
#         tokens = [lemma.lower() if lemma != '<unknown>' else token.lower() for token, tag, lemma in tokens if tag == PreprocessWorker.noun[lan2]]
#         if(len(tokens) == 0):
#             continue            
#         translation = tokens[0]   
        if dict2.has_key(translation) and not dictOutput.has_key(key) and key != translation and sp1.row2id.has_key(key) and sp2.row2id.has_key(translation):
            dictOutput[key] = translation
            print str(counter) + ". " + key + " - " + translation
            counter += 1
            if counter == num*3:
                break
                        
    json.dump(dict(random.sample(dictOutput.items(), num)), codecs.open(dictFileOutput, 'w', encoding='utf8'), ensure_ascii=False)    

    
def main(sys_argv):
    try:
        opts, argv = getopt.getopt(sys_argv[1:], 'h', ["help"])
    except getopt.GetoptError, err:
        print str(err)
        usage()
        sys.exit(1)
    
    for opt in opts:
        if opt in ("-h", "--help"):
            usage(0)
        else:
            usage(1)
            
    if len(argv) == 4:
        try:
            directory = sys.argv[1]
            lan1 = sys.argv[2]
            lan2 = sys.argv[3]        
            n = int(sys.argv[4])
            
            create_dict(directory, lan1, lan2, n)
        except ValueError:
            print "n needs to be integer"
            usage(1)        
    else:
        print "Invalid number of arguments"
        usage(1)

if __name__ == '__main__':
    main(sys.argv)
