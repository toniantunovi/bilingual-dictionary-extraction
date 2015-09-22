import codecs
import collections
import getopt
import json
import numpy as np
import sys

from space import Space
from utils import score, get_valid_data


def usage(errno=0):
    print >> sys.stderr, \
    """
    Calculate precision of AE model given word2vec vectors of pseudodocument, learned weights for autoencoder (AE),
    dictionary files and test set.
    
    Usage:
    python test_ae.py word2vec_file weights_file dict1 dict2 test_set
    python test_ae.py --help
    
    Options:
    -h --help: help
    
    Arguments:
    word2vec_file: <file>, vectors produced by word2vec on pseudodocument
    weights_file: <file>, weights learned for sparsed autoencoder
    dict1: <file>, dictionary for the first language
    dict2: <file>, dictionary for the second language
    test_set: <file>, test set
    
    Examples:
    1) Calculate precision of trained model on given test set
    
    python test_ae.py Data/vec_deit.txt Data/weights.txt Data/dict_de.txt Data/dict_it.txt Data/test_deit.txt
    
    """
    sys.exit(errno)
    
def sigmoid(x):
    return (1 / (1 + np.exp(-x)))

def test_ae(word2vecFile, weightsFile, dictFile1, dictFile2, goldFile, printInfo=False):
    print "Testing..."
    dict1 = json.load(codecs.open(dictFile1, 'r', encoding='utf8'))
    dict2 = json.load(codecs.open(dictFile2, 'r', encoding='utf8'))
    test_data = json.load(codecs.open(goldFile, 'r', encoding='utf8'))
    
    if printInfo:
        print "Removing double entries..."
    for key in dict2.keys():
        if dict1.has_key(key):
            dict2.pop(key, None)
    
    if printInfo:   
        print "Building source vector space..."
    source_words = set(test_data.keys())    
    source_sp = Space.build(word2vecFile, source_words)
    
    if printInfo:    
        print "Building target vector space..."
    target_words = set(dict2.keys())
    target_sp = Space.build(word2vecFile, target_words)
        
    if printInfo:
        print "Loading autoencoder weights matrix..."
    W = np.loadtxt(weightsFile)
    
    source_sp.mat = np.dot(W, source_sp.mat.transpose()).transpose()
    target_sp.mat = np.dot(W, target_sp.mat.transpose()).transpose()
    
    source_sp.normalize()
    target_sp.normalize()
    
    test_data = [(k, v) for k, v in test_data.iteritems()]
    test_data = get_valid_data(source_sp, target_sp, test_data)
    
    gold = collections.defaultdict(set)
    for k, v in test_data:
        gold[k].add(v)
    
    return score(source_sp, target_sp, gold, None, printInfo)
    
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
            
    if len(argv) == 5:
        word2vecFile = sys_argv[1]
        weightsFile = sys_argv[2]
        dictFile1 = sys_argv[3]
        dictFile2 = sys_argv[4]
        goldFile = sys_argv[5]
        
        test_ae(word2vecFile, weightsFile, dictFile1, dictFile2, goldFile, True)
    else:
        usage(1)

if (__name__ == '__main__'):
    main(sys.argv)

