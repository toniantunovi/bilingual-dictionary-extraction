import sys
import codecs
import getopt
from word2vec import word2vec
from create_training_set import create_training_set
from train_tm import train_translation_matrix
from test_tm import test_tm
from test_basic import test_basic

def usage(errno=0):
    print >> sys.stderr, \
    """
    Run full test on model that takes input from unsupervised Vulic model and uses it as training set for 
    supervised Mikolov
    
    Hyperparameters:    
    - n - number of words to be used when creating training set for translation matrix
    - p - similarity threshold
     
    Usage:
    python test_model.py lan1 lan2
    python test_model.py --help
    
    Options:
    -h --help: help
    
    Arguments:
    lan1, lan2: language codes (en - english, de - german, es - spanish, fr - french, it - italian, hr - croatian)
        
    Examples:
    1) Run full tests on enit corpora    
    python test_model.py en it    
    
    2) Show help:
    python test_model.py --help
    """
    sys.exit(errno)

def get_word2vec_opts(input, output, cbow, size, window):
    word2vecOpts = list()
    word2vecOpts.append("-train")
    word2vecOpts.append(input)
    word2vecOpts.append("-output")
    word2vecOpts.append(output)
    word2vecOpts.append("-cbow")
    word2vecOpts.append(str(cbow))
    word2vecOpts.append("-size")
    word2vecOpts.append(str(size))
    word2vecOpts.append("-window")
    word2vecOpts.append(str(window))
    return word2vecOpts
    
def output_score(fOut, score, n, p):
    fOut.write("n=" + str(n) + ", p=" + str(p) + "\n")
    fOut.write("prec@1:" + str(score[0]) + ", prec@5:" + str(score[1]) + ", prec@10:" + str(score[2]) + "\n\n")
    
def test(lan1, lan2, directory):   
    inputFile = directory + "text_" + lan1 + lan2 + ".txt"
    inputFile1 = directory + "text_" + lan1 + ".txt"
    inputFile2 = directory + "text_" + lan2 + ".txt" 
    word2vecFile = directory + "vec_" + lan1 + lan2 + ".txt"
    word2vecFile1 = directory + "vec_" + lan1 + ".txt"
    word2vecFile2 = directory + "vec_" + lan2 + ".txt"
    dictFile1 = directory + "dict_" + lan1 + ".txt"
    dictFile2 = directory + "dict_" + lan2 + ".txt"
    goldFile = directory + "dict_" + lan1 + lan2 + ".txt"
    tmFile = directory + "tm.txt"
    trainingSetFile = directory + "training_set.txt"
    testResultsFile = directory + "test_results.model.txt"
    fOut = codecs.open(testResultsFile, 'w', encoding='utf8')

    n = [1000, 5000, 7000, 10000]
    p = [0.7, 0.8, 0.9]
    d = 50  
    cs = 5
    
    word2vecOpts = get_word2vec_opts(inputFile, word2vecFile, 0, d, cs)
    word2vec(word2vecOpts)
    word2vecOpts = get_word2vec_opts(inputFile1, word2vecFile1, 0, d, cs)
    word2vec(word2vecOpts)
    word2vecOpts = get_word2vec_opts(inputFile2, word2vecFile2, 0, d, cs)
    word2vec(word2vecOpts)

    print "\nTesting model...\n"
    score = test_basic(word2vecFile, dictFile1, dictFile2, goldFile)
    output_score(fOut, score, 0, 0)
    for hp1 in n:
        for hp2 in p:
            create_training_set(word2vecFile, dictFile1, dictFile2, trainingSetFile, hp1, hp2)
            train_translation_matrix(trainingSetFile, word2vecFile1, word2vecFile2, tmFile)
            score = test_tm(False, tmFile, goldFile, word2vecFile1, word2vecFile2, dictFile1, dictFile2)   
            
            print "n: " + str(hp1) + ", p: " + str(hp2) + ", score: " + str(score) + "\n"
            output_score(fOut, score, hp1, hp2)


def test_full(lan1, lan2):
    directory_s = "Data/" + lan1 + lan2 + "/output/"
    directory_r = "Data/" + lan1 + lan2 + "/output_r/"
    
    test(lan1, lan2, directory_s)
    test(lan1, lan2, directory_r)
        
def main(sys_argv):
    try:
        opts, argv = getopt.getopt(sys_argv[1:], 'h', ["help"])
    except getopt.GetoptError, err:
        print str(err)
        usage()
        sys.exit(1)
    
    for opt, val in opts:
        print opt
        if opt in ("-h", "--help"):
            usage(0)
        else:
            usage(1)
            
    if len(argv) == 2:
        lan1 = sys_argv[1]
        lan2 = sys_argv[2]
        
        test_full(lan1, lan2)
        
    else:
        print "Invalid number of arguments"
        usage(1)

if (__name__ == '__main__'):
    main(sys.argv)

