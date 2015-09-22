import sys
import getopt
import numpy as np
import collections
import random
import json
import codecs
from space import Space
from create_training_set import clean_dictionaries
from utils import read_dict, apply_tm, score, get_valid_data

def usage(errno=0):
    print >>sys.stderr,\
    """
    Given a translation matrix, test data (words and their translations) and 
    source and target language vectors, it returns translations of source test 
    words and computes Top N accuracy.

    Usage:
    python test_tm.py [options] trans_matrix test_data source_vecs target_vecs
    \n\
    Options:
    -o --output <file>: file prefix. It prints the vectors obtained after 
                        the translation matrix is applied (.vecs.txt and .wds.txt).
                        Optional. Default is ./translated_vecs
    -c --correction <int>: Number of additional elements (ADDITIONAL TO TEST DATA)
                         to be used with Global Correction (GC) strategy. 
                         Optional. Default, baseline retrieval is run.
                          
    -h --help : help

    Arguments:
    trans_matrix: <file>, translation matrix
    test_data: <file>, list of source-target word pairs (space separated words, 
                one word pair per line)
    source_vecs: <file>, vectors in source language, Space-separated, with string 
                identifier as first column (dim+1 columns, where dim is the 
                dimensionality of the space)
    target_vecs: <file>, vectors in target language


    Example:
    1) Retrieve translations with standard nearest neighbour retrieval

    python test_tm.py tm.txt test_data.txt ENspace.txt ITspace.txt
    
    2) "Corrected" retrieval (GC). Use additional 2000 source space elements to 
    correct for hubs (words that appear as the nearest neighbours of many points))

    python -c 2000 test_tm.py tm.txt test_data.txt ENspace.txt ITspace.txt

    """
    sys.exit(errno)
    
def test_tm(additional, tm_file, test_file, source_file, target_file, dictFile1, dictFile2):    
    dict1 = json.load(codecs.open(dictFile1, 'r', encoding='utf8'))
    dict2 = json.load(codecs.open(dictFile2, 'r', encoding='utf8'))
    clean_dictionaries(dict1, dict2)
    
    print "Loading the translation matrix"
    tm = np.loadtxt(tm_file)

    print "Reading the test data"
    test_data = read_dict(test_file)
    
    #in the _source_ space, we only need to load vectors for the words in test.
    #semantic spaces may contain additional words, ALL words in the _target_ 
    #space are used as the search space
    source_words, _ = zip(*test_data)
    source_words = set(source_words)

    print "Reading: %s" % source_file
    if not additional:
        source_sp = Space.build(source_file, source_words)
    else:
        #read all the words in the space
        lexicon = set(np.loadtxt(source_file, skiprows=1, dtype=str, 
                                    comments=None, usecols=(0,)).flatten())
        #the max number of additional+test elements is bounded by the size 
        #of the lexicon
        additional = min(additional, len(lexicon) - len(source_words))
        #we sample additional elements that are not already in source_words
        random.seed(100)
        lexicon = random.sample(list(lexicon.difference(source_words)), additional)
        
        #load the source space
        source_sp = Space.build(source_file, source_words.union(set(lexicon)))
    
#     source_sp.normalize()

    print "Reading: %s" % target_file
    print "target_file: " + target_file
    target_words = set(dict2.keys())
    target_sp = Space.build(target_file, target_words)
    target_sp.normalize()

    print "Translating" #translates all the elements loaded in the source space
    mapped_source_sp = apply_tm(source_sp, tm)
    
    print "Retrieving translations"
    test_data = get_valid_data(source_sp, target_sp, test_data)

    #turn test data into a dictionary (a word can have mutiple translation)
    gold = collections.defaultdict(set)
    for k, v in test_data:
        gold[k].add(v)

    return score(mapped_source_sp, target_sp, gold, additional, True)


def main(sys_argv):

    try:
        opts, argv = getopt.getopt(sys_argv[1:], "ho:c:",
                                   ["help", "output=", "correction="])
    except getopt.GetoptError, err:
        print str(err)
        usage()
        sys.exit(1)

    additional = None
    for opt, val in opts:
        if opt in ("-o", "--ouput"):
            out_file = val
        if opt in ("-c", "--correction"):
            try:
                additional = int(val)
            except ValueError:
                usage(1)
        elif opt in ("-h", "--help"):
            usage(0)
        else:
            usage(1)

    if len(argv) == 6:
        tm_file = argv[0]
        test_file = argv[1]
        source_file = argv[2]
        target_file = argv[3]
        dictFile1 = argv[4]
        dictFile2 = argv[5]

    else:
        print str(err)
        usage(1)

    test_tm(additional, tm_file, test_file, source_file, target_file, dictFile1, dictFile2)

if __name__ == '__main__':
    main(sys.argv)

