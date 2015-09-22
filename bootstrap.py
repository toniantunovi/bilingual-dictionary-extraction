import sys
import json
import codecs
import getopt
import random
import numpy as np
from space import Space

def usage(errno=0):
    print >> sys.stderr, \
    """
    Bootstrap input file
    
    Creates output file which is a bootstrapped version of input created by taking
    n most frequent words in input and for each one of them their k most probable
    translations and adds one of them each time that word appears in input text
    
    Usage:
    python bootstrap.py word2vecFile dictFile1 dictFile2 inputFile outputFile n k
    python bootstrap.py --help
    
    Options:
    -h --help: help
    
    Arguments:
    word2vecFile: word2vec vectors trained on inputFile
    dictFile1: dictionary containing words from language 1 and their frequency in inputFile
    dictFile2: dictionary containing words from language 2 and their frequency in inputFile
    inputFile: pseudodocument created by preprocess.py and used to train word2vec
    outputFile: bootstrapped pseudodocument
    n: number of most frequent words to be used
    k: number of most probable translations for each of n words
    
    Examples:
    1) Bootstrap enit smart initialized   
    python bootstrap.py Data/enit/output/vec_enit.txt Data/enit/output/dict_en.txt Data/enit/output/dict_it.txt
        Data/enit/output/text_enit.txt Data/enit/output/text_enit.bootstrap1.txt
    
    2) Show help:
    python bootstrap.py --help
    """
    sys.exit(errno)

def weighted_random_choice(choices):
    max = sum(choices.values())
    pick = random.uniform(0, max)
    current = 0
    for key, value in choices.items():
        current += value
        if current > pick:
            return key

def write_pseudodocument(words1, words2, inputFile, outputFile):
    fOut = codecs.open(outputFile, 'w', encoding='utf-8')
    
    with codecs.open(inputFile, 'r', encoding='utf8') as fIn:
        line = ''
        for line in fIn:        
            tokens1 = line.split(" ")
            tokens2 = []
            for token in tokens1:
                if words1.has_key(token):
                    tokens2.append(token)
                    addedWord = weighted_random_choice(words1[token])
                    tokens2.append(addedWord)
                elif words2.has_key(token):
                    tokens2.append(token)
                    addedWord = weighted_random_choice(words2[token])
                    tokens2.append(addedWord)
                else:
                    tokens2.append(token)
                            
            fOut.write(' '.join(tokens2) + "\n")
            
    fOut.close()
    
def get_similar_words(word2vecFile, dictFile1, dictFile2, n, k):
    dict1 = json.load(codecs.open(dictFile1, 'r', encoding='utf8'))
    dict2 = json.load(codecs.open(dictFile2, 'r', encoding='utf8'))
    
    for key in dict2.keys():
        if dict1.has_key(key):
            dict2.pop(key, None)    
    
    # Getting n most frequent words
    source_words = []
    counter = 0
    for key, value in sorted(dict1.iteritems(), key=lambda (k, v): (v, k), reverse=True):
        source_words.append(key)
        counter += 1
        if counter == n:
            break
        
    print "Got " + str(n) + " most frequent words"
    # print source_words
    
    # Building source vector space
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
    words = dict()
    for i,el1 in enumerate(sp1.id2row):
        sp1_idx = sp1.row2id[el1]
        words[el1] = dict()
        
        for j in range(k):
            sp2_idx = srtd_idx[j, sp1_idx]
            word = sp2.id2row[sp2_idx]
            words[el1][word] = -sim_mat[sp2_idx, sp1_idx] 
            
    return words


def bootstrap(word2vecFile, dictFile1, dictFile2, inputFile, outputFile, n, k):    
    print "Bootstrapping..."
    words1 = get_similar_words(word2vecFile, dictFile1, dictFile2, n, k)
    words2 = get_similar_words(word2vecFile, dictFile2, dictFile1, n, k)
    
    print "Got "+str(k)+" nearest neighbours for each of "+str(n)+" most frequent words for both languages"
    
    print "Writing pseudodoument..."
    write_pseudodocument(words1, words2, inputFile, outputFile)
    
    
def main(sys_argv):
    try:
        opts, argv = getopt.getopt(sys_argv[1:], 'h', ["help"])
    except getopt.GetoptError, err:
        print str(err)
        usage()
        sys.exit(1)
    
    for opt, val in opts:
        if opt in ("-h", "--help"):
            usage(0)
        else:
            usage(1)
            
    if len(argv) == 7:
        try:
            word2vecFile = sys_argv[1]
            dictFile1 = sys_argv[2]
            dictFile2 = sys_argv[3]
            inputFile = sys_argv[4]
            outputFile = sys_argv[5]
            n = int(sys_argv[6])
            k = int(sys_argv[7])
        
            bootstrap(word2vecFile, dictFile1, dictFile2, inputFile, outputFile, n, k)
        except ValueError:
            print >> sys.stderr, "Error: n and k parameters need to be integers"
            usage(1)        
    else:
        usage(1)
    
    
if (__name__ == '__main__'):
    main(sys.argv)
    