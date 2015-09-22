import codecs
import collections
import getopt
import json
import sys

from space import Space
from utils import score, get_valid_data


def usage(errno=0):
    print >> sys.stderr, \
    """
    Calculate precision of basic model given word2vec vectors of pseudodocument, dictionary files and test set.
    
    Usage:
    python test_basic.py word2vec_file dict1 dict2 test_set
    python test_basic.py --help
    
    Options:
    -h --help: help
    
    Arguments:
    word2vec: <file>, vectors produced by word2vec on pseudodocument
    dict1: <file>, dictionary for the first language
    dict2: <file>, dictionary for the second language
    test_set: <file>, test set
    
    Examples:
    1) Calculate precision of trained model on given test set
    
    python test_basic.py Data/vec_deit.txt Data/dict_de.txt Data/dict_it.txt Data/test_deit.txt
    
    """
    sys.exit(errno)

def test_basic(word2vecFile, dictFile1, dictFile2, goldFile, printInfo=False):
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
            
    if len(argv) == 4:
        word2vecFile = sys_argv[1]
        dictFile1 = sys_argv[2]
        dictFile2 = sys_argv[3]
        goldFile = sys_argv[4]
        
        test_basic(word2vecFile, dictFile1, dictFile2, goldFile, True)
    else:
        usage(1)

if (__name__ == '__main__'):
    main(sys.argv)

