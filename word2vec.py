import sys
import subprocess
import getopt

def usage(errno=0):
    print >> sys.stderr, \
    """
    Python wrapper for word2vec
    
    Tools for computing distributed representions of words
    ------------------------------------------------------
    
    Given a text corpus, the word2vec tool learns a vector for every word in the vocabulary using the Continuous
    Bag-of-Words or the Skip-Gram neural network architectures. The user should to specify the following:
     - desired vector dimensionality
     - the size of the context window for either the Skip-Gram or the Continuous Bag-of-Words model
     - training algorithm: hierarchical softmax and / or negative sampling
     - threshold for downsampling the frequent words 
     - number of threads to use
     - the format of the output word vector file (text or binary)
    
    Usually, the other hyper-parameters such as the learning rate do not need to be tuned for different training sets. 
     
    Options:
    Parameters for training:
        --train=<file>
            Use text data from <file> to train the model
        --output=<file>
            Use <file> to save the resulting word vectors / word clusters
        --size=<int>
            Set size of word vectors; default is 100
        --window=<int>    
            Set max skip length between words; default is 5
        --sample=<float>
            Set threshold for occurrence of words. Those that appear with higher frequency in the training data
            will be randomly down-sampled; default is 1e-3, useful range is (0, 1e-5)
        --hs=<int>
            Use Hierarchical Softmax; default is 0 (not used)
        --negative=<int>
            Number of negative examples; default is 5, common values are 3 - 10 (0 = not used)
        --threads=<int>
            Use <int> threads (default 12)
        --iter=<int>
            Run more training iterations (default 5)
        --min-count=<int>
            This will discard words that appear less than <int> times; default is 5
        --alpha=<float>
            Set the starting learning rate; default is 0.025 for skip-gram and 0.05 for CBOW
        --classes=<int>
            Output word classes rather than word vectors; default number of classes is 0 (vectors are written)
        --debug=<int>
            Set the debug mode (default = 2 = more info during training)
        --binary=<int>
            Save the resulting vectors in binary moded; default is 0 (off)
        --save-vocab=<file>
            The vocabulary will be saved to <file>
        --read-vocab=<file>
            The vocabulary will be read from <file>, not constructed from the training data
        --cbow=<int>
            Use the continuous bag of words model; default is 1 (use 0 for skip-gram model)
    
    Examples:
    python word2vec.py --train=data.txt --output=vec.txt --size=200 --window=5 --sample=1e-4 --negative=5 --hs=0 --binary=0 --cbow=1 --iter=3

    """
    sys.exit(errno)
    
def word2vec(opts):
    subprocess.call(["word2vec/word2vec"] + opts)
    
def main(sys_argv):
    try:
        opts, argv = getopt.getopt(sys_argv[1:], "", ["train=", "output=", "size=", "window=",
                                          "sample=", "hs=", "negative=", "threads=", "iter=", "min-count=",
                                          "alpha=", "classes=", "debug=", "binary=", "save-vocab=",
                                          "read-vocab=", "cbow="])
    except getopt.GetoptError, err:
        print >> sys.stderr, "Error: Incorrect options"
        usage()
        sys.exit(1)
        
    
    word2vecOpts = list()
    for opt, val in opts:
        if opt == "--train":
            word2vecOpts.append("-train")
            word2vecOpts.append(val)
        elif opt == "--output":
            word2vecOpts.append("-output")
            word2vecOpts.append(val)
        elif opt == "--size":
            try:
                n = int(val)
                word2vecOpts.append("-size")
                word2vecOpts.append(str(n))
            except ValueError:
                print >> sys.stderr, "Error: size"
                usage(1)
        elif opt == "--window":
            try:
                n = int(val)
                word2vecOpts.append("-window")
                word2vecOpts.append(str(n))
            except ValueError:
                print >> sys.stderr, "Error: window"
                usage(1)
        elif opt == "--sample":
            try:
                n = float(val)
                word2vecOpts.append("-sample")
                word2vecOpts.append(str(n))
            except ValueError:
                print >> sys.stderr, "Error: sample"
                usage(1)
        elif opt == "--hs":
            try:
                n = int(val)
                word2vecOpts.append("-hs")
                word2vecOpts.append(str(n))
            except ValueError:
                print >> sys.stderr, "Error: hs"
                usage(1)
        elif opt == "--negative":
            try:
                n = int(val)
                word2vecOpts.append("-negative")
                word2vecOpts.append(str(n))
            except ValueError:
                print >> sys.stderr, "Error: negative"
                usage(1)
        elif opt == "--threads":
            try:
                n = int(val)
                word2vecOpts.append("-threads")
                word2vecOpts.append(str(n))
            except ValueError:                
                print >> sys.stderr, "Error: threads"
                usage(1)
        elif opt == "--iter":
            try:
                n = int(val)
                word2vecOpts.append("-iter")
                word2vecOpts.append(str(n))
            except ValueError:
                print >> sys.stderr, "Error: iter"
                usage(1)
        elif opt == "--min-count":
            try:
                n = int(val)
                word2vecOpts.append("-min-count")
                word2vecOpts.append(str(n))
            except ValueError:                
                print >> sys.stderr, "Error: min-count"
                usage(1)
        elif opt == "--alpha":
            try:
                n = float(val)
                word2vecOpts.append("-alpha")
                word2vecOpts.append(str(n))
            except ValueError:
                print >> sys.stderr, "Error: alpha"
                usage(1)
        elif opt == "--classes":
            try:
                n = int(val)
                word2vecOpts.append("-classes")
                word2vecOpts.append(str(n))
            except ValueError:
                print >> sys.stderr, "Error: classes"
                usage(1)
        elif opt == "--debug":
            try:
                n = int(val)
                word2vecOpts.append("-debug")
                word2vecOpts.append(str(n))
            except ValueError:
                print >> sys.stderr, "Error: debug"
                usage(1)
        elif opt == "--binary":
            try:
                n = int(val)
                word2vecOpts.append("-binary")
                word2vecOpts.append(str(n))
            except ValueError:
                print >> sys.stderr, "Error: binary"
                usage(1)
        elif opt == "--save-vocab":
            word2vecOpts.append("-save-vocab")
            word2vecOpts.append(val)
        elif opt == "--read-vocab":
            word2vecOpts.append("-read-vocab")
            word2vecOpts.append(val)
        elif opt == "--cbow":
            try:
                n = int(val)
                word2vecOpts.append("-cbow")
                word2vecOpts.append(str(n))
            except ValueError:
                print >> sys.stderr, "Error: cbow"
                usage(1)
        
    if len(word2vecOpts) > 1:
        word2vec(word2vecOpts)
    else:
        print >> sys.stderr, "Error: No options"
        usage(1)

if (__name__ == "__main__"):
    main(sys.argv)
