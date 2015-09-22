import sys
import codecs
import getopt
from word2vec import word2vec
from test_basic import test_basic
from bootstrap import bootstrap    

def usage(errno=0):
    print >> sys.stderr, \
    """
    Run full test 
    Output to files results of testing Random shuffling initialized model (R model), 
    Smart initialized model (S model) and Model with bootstraping for both types of initialization.
    
    Hyperparameters for R and S models:    
    - word2vec:
        - CBOW or skip-gram
        - d - length of generated word vectors
        - cs - context window size
        
    Additional hyperparameters for bootstrapping:
        - n - number of most frequent words for which translations will be inserted
        - k - number of translations for each word from which inserted one will be chosen
    
    Usage:
    python test_full.py lan1 lan2
    python test_full.py --help
    
    Options:
    -h --help: help
    -b --bootstrap: test bootstrapping
    
    Arguments:
    lan1, lan2: language codes (en - english, de - german, es - spanish, fr - french, it - italian, hr - croatian)
        
    Examples:
    1) Run full tests on enit corpora    
    python test_full.py en it    
    
    2) Show help:
    python test_full.py --help
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
    
def output_score(fOut, score, cbow, d, cs):
    fOut.write("cbow=" + str(cbow) + ", d=" + str(d) + ", cs=" + str(cs) + "\n")
    fOut.write("prec@1:" + str(score[0]) + ", prec@5:" + str(score[1]) + ", prec@10:" + str(score[2]) + "\n\n")
    
def output_score_bootstrap(fOut, score, n, k):
    fOut.write("n=" + str(n) + ", k=" + str(k) + "\n")
    fOut.write("prec@1:" + str(score[0]) + ", prec@5:" + str(score[1]) + ", prec@10:" + str(score[2]) + "\n\n")
    
def test(lan1, lan2, directory):   
    inputFile = directory + "text_" + lan1 + lan2 + ".txt"
    word2vecFile = directory + "vec_" + lan1 + lan2 + ".txt"
    dictFile1 = directory + "dict_" + lan1 + ".txt"
    dictFile2 = directory + "dict_" + lan2 + ".txt"
    goldFile = directory + "dict_" + lan1 + lan2 + ".txt"
    testResultsFile = directory + "test_results.txt"
    fOut = codecs.open(testResultsFile, 'w', encoding='utf8')
    
    cbow = [0, 1]
    d = [50, 100, 150, 200, 250, 300]
    cs = [5, 16, 48]
#     d = [200, 250, 300]
#     cs = [64, 96, 128]
    
    for hp1 in cbow:
        for hp2 in d:
            for hp3 in cs:
                word2vecOpts = get_word2vec_opts(inputFile, word2vecFile, hp1, hp2, hp3)
                word2vec(word2vecOpts)
                print "\nTesting..."
                score = test_basic(word2vecFile, dictFile1, dictFile2, goldFile)
                print "Score: " + str(score) + "\n"
                output_score(fOut, score, hp1, hp2, hp3)
    
    
def test_bootstrap(lan1, lan2, directory):
    word2vecFile = directory + "vec_" + lan1 + lan2 + ".txt"
    dictFile1 = directory + "dict_" + lan1 + ".txt"
    dictFile2 = directory + "dict_" + lan2 + ".txt"
    goldFile = directory + "dict_" + lan1 + lan2 + ".txt"
    inputFile = directory + "text_" + lan1 + lan2 + ".txt"
    bootstrapedFile = directory + "text_" + lan1 + lan2 + ".bootstrap.txt"
    n = [100, 1000]
    k = [5, 10]
    d = 50
    cs = 5
    testResultsFile = directory + "test_results.bootstrap.txt"
    fOut = codecs.open(testResultsFile, 'w', encoding='utf8')
    
    word2vecOpts = get_word2vec_opts(inputFile, word2vecFile, 0, d, cs)
    word2vec(word2vecOpts)
    score = test_basic(word2vecFile, dictFile1, dictFile2, goldFile)
    newScore = score
    output_score_bootstrap(fOut, score, 0, 0)    
    for hp1 in n:
        for hp2 in k:         
            iteration = 0
            while newScore >= score:
                iteration += 1                
                score = newScore
                bootstrap(word2vecFile, dictFile1, dictFile2, inputFile, bootstrapedFile, hp1, hp2)                
                word2vecOpts = get_word2vec_opts(bootstrapedFile, word2vecFile, 0, d, cs)
                word2vec(word2vecOpts)
                newScore = test_basic(word2vecFile, dictFile1, dictFile2, goldFile)
                print "Iteration: " + str(iteration) + ", Score: " + str(newScore)
            output_score_bootstrap(fOut, newScore, hp1, hp2) # variable score should be here in the place of newScore
            newScore = score

def test_full(lan1, lan2, bFlag):
    directory_s = "Data/" + lan1 + lan2 + "/output/"
    directory_r = "Data/" + lan1 + lan2 + "/output_r/"
    
    if not bFlag:
        test(lan1, lan2, directory_s)
        test(lan1, lan2, directory_r)
    else:
        test_bootstrap(lan1, lan2, directory_s)
        test_bootstrap(lan1, lan2, directory_r)
    
    
def main(sys_argv):
    try:
        opts, argv = getopt.getopt(sys_argv[1:], 'b:h', ["bootstrap", "help"])
    except getopt.GetoptError, err:
        print str(err)
        usage()
        sys.exit(1)
    
    bFlag = False
    for opt, val in opts:
        print opt
        if opt in ("-h", "--help"):
            usage(0)
        elif opt in ("-b", "--bootstrap"):
            bFlag = True
        else:
            usage(1)
            
    if len(argv) == 2:
        lan1 = sys_argv[1]
        lan2 = sys_argv[2]
        
        test_full(lan1, lan2, bFlag)
        
    else:
        print "Invalid number of arguments"
        usage(1)

if (__name__ == '__main__'):
    main(sys.argv)

