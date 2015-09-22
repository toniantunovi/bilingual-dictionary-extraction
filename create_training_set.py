# coding: utf-8

import sys
import getopt
import json
import codecs
import random
import numpy as np
import copy
import gc
import re
from space import Space

def usage(errno=0):
    print >> sys.stderr, \
    """
    Create training set for TM (translation matrix) using n most frequent words
        
    Usage:
    pythong create_training_set word2vecFile dictFile1 dictFile2 outputDict n p
    python bootstrap.py --help
    
    Options:
    -h --help: help
    
    Arguments:
    word2vecFile: word2vec vectors
    dictFile1: dictionary containing words from language 1 and their frequency in inputFile
    dictFile2: dictionary containing words from language 2 and their frequency in inputFile
    outputDict: training set
    n: number of most frequent words to be used
    p: similarity threshold - p in [0,1]
    
    Examples:
    1) Create training set for enit with n = 5000 words and threshold similarity 0.65 
    python create_training_set.py Data/enit/output/vec_enit.txt Data/enit/output/dict_en.txt Data/enit/output/dict_it.txt Data/enit/output/training_set.txt 5000 0.65
    
    2) Show help:
    python test_full.py --help
    """
    sys.exit(errno)
    
def clean_dictionaries(dict1, dict2):
    print "Cleaning dictionaries..."
    dict2_copy = copy.deepcopy(dict2)
    
    for key in dict2_copy.keys():
        if dict1.has_key(key):
            dict2.pop(key, None)
   
        elif re.search(r"[^a-zA-Z]", key) is not None or len(key) < 3:
            dict2.pop(key, None)
           
    for key in dict1.keys():
        if re.search(r"[^a-zA-Z]", key) is not None or len(key) < 3:
           dict1.pop(key, None)
           
def get_dictionary(word2vecFile, dict1, dict2, n, p):        
    # Getting n most frequent words
    source_words = []
    counter = 0
    for key, value in sorted(dict1.iteritems(), key=lambda (k, v): (v, k), reverse=True):
        source_words.append(key)
        counter += 1
        if counter == n:
            break
            
    print "Got " + str(len(source_words)) + " most frequent words"
        
    # Building source vector space
#     source_words = random.sample(source_words, n)
    source_words = set(source_words)
    sp1 = Space.build(word2vecFile, source_words)
    
    # Building target vector space
    target_words = set(dict2.keys())
    sp2 = Space.build(word2vecFile, target_words)
        
    print "Calculating and sorting similarity matrix..."
    # Calculating and sorting similarity matrix
    sp1.normalize()
    sp2.normalize()
    sim_mat = -sp2.mat*sp1.mat.T
    srtd_idx = np.argsort(sim_mat, axis=0)
    
    # Adding k most similar words to each of n selected words
    dictOutput = dict()
    for i,el1 in enumerate(sp1.id2row):
        sp1_idx = sp1.row2id[el1]
        sp2_idx = srtd_idx[0, sp1_idx]
        sp2_idx2 = srtd_idx[1, sp1_idx]
        if -sim_mat[sp2_idx, sp1_idx] > p:
            print "1: " + str(-sim_mat[sp2_idx, sp1_idx]) + ", 2: " + str(-sim_mat[sp2_idx2, sp1_idx]) + ". word1: " + el1 + ", word2: " + sp2.id2row[sp2_idx]
            dictOutput[el1] = sp2.id2row[sp2_idx]      
   
    return dictOutput

def create_training_set(word2vecFile, dictFile1, dictFile2, dictFileOutput, n, p):
    
    print "Creating training set..."
    
    dict1 = json.load(codecs.open(dictFile1, 'r', encoding='utf8'))
    dict2 = json.load(codecs.open(dictFile2, 'r', encoding='utf8'))
    dictOutput = dict()
    clean_dictionaries(dict1, dict2)
    
    dictOutput1 = get_dictionary(word2vecFile, dict1, dict2, n, p)
    dictOutput2 = get_dictionary(word2vecFile, dict2, dict1, n, p)

    dictOutput.update(dictOutput1)
                        
    for key, value in dictOutput1.iteritems():
        if dictOutput2.has_key(value) and dictOutput2[value] == key:
            dictOutput[key] = value
                        
    print "Created training set. Outputing " + str(len(dictOutput)) + " items as dictionary."
    json.dump(dictOutput, codecs.open(dictFileOutput, 'w', encoding='utf8'), ensure_ascii=False)
 
    
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
    print "len(argv): " + str(len(argv))	            
    if len(argv) == 6:
        try:
            word2vecFile = sys_argv[1]
            dictFile1 = sys_argv[2]
            dictFile2 = sys_argv[3]
            dictFileOutput = sys_argv[4]
            n = int(sys_argv[5])
            p = float(sys_argv[6])
        
            create_training_set(word2vecFile, dictFile1, dictFile2, dictFileOutput, n, p)
        except ValueError:
            print >> sys.stderr, "Error: n needs to be integer, p needs to be float"
            usage(1)        
    else:
        print >> sys.stderr, "Error: Invalid number of parameters"
        usage(1)
    
    
if (__name__ == '__main__'):
    main(sys.argv)