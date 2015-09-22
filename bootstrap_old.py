import sys
import codecs
import numpy as np
import json
import os
from space import Space
from test_basic import test_basic
from word2vec import word2vec

def write_pseudodocument(words, inputFile, outputFile):
    fOut = codecs.open(outputFile, 'w', encoding='utf-8')
    
    with codecs.open(inputFile, 'r', encoding='utf8') as fIn:
        continueRead = True
        line = ''
        # In the first version of preprocessing script everything was written to file without newlines
        # Because of that reading is implemented this way
        while continueRead:
            tokens1 = []
            counter = 0
            while counter < 1000:
                word, space, line = line.partition(' ')
                if space:
                    tokens1.append(word)
                    counter += 1
                else:
                    next_chunk = fIn.read(1000)
                    if next_chunk:
                        line = word + next_chunk
                    else:
                        tokens1.append(word.rstrip('\n'))
                        continueRead = False
                        break
                        
            tokens2 = []
            for token in tokens1:
                if words.has_key(token):
                    center_pos = len(words[token])/2
                    words[token].insert(center_pos, token)
                    tokens2.extend(words[token])
                else:
                    tokens2.append(token)
	                        
            fOut.write(' '.join(tokens2) + " ")
            
    fOut.close()
            

def create_pseudodocument(word2vecFile1, dictFile1, dictFile2, inputFile, outputFile, n, k, word2vecFile2 = None):
    dict1 = json.load(codecs.open(dictFile1, 'r', encoding='utf8'))
    dict2 = json.load(codecs.open(dictFile2, 'r', encoding='utf8'))
    
    print "Creating pseudodocument..."
    
    for key in dict2.keys():
        if dict1.has_key(key):
            dict2.pop(key, None)    
    
    # Getting n most frequent words
    source_words = []
    counter = 0
    for key, value in sorted(dict1.iteritems(), key=lambda (k, v): (v, k), reverse=True):
        source_words.append(key)
        print "Key = " + key + ", value = " + str(value)
        counter += 1
        if counter == n:
            break
        
    print "Got the words"
    print source_words
    
    # Building source vector space
    source_words = set(source_words)
    sp1 = Space.build(word2vecFile1, source_words)
    
    # Building target vector space
    target_words = set(dict2.keys())
    if word2vecFile2 is None:
        sp2 = Space.build(word2vecFile1, target_words)
    else:
        sp2 = Space.build(word2vecFile2, target_words)
        
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
        
        for j in range(k):
            sp2_idx = srtd_idx[j, sp1_idx]
            word = sp2.id2row[sp2_idx]
            dict2[word] += dict1[el1]
            if(words.has_key(el1)):
                words[el1].append(word)
            else:
                words[el1] = [word]
            
    print "Got " + str(k) + " nearest neighbours for each of " + str(n) + " most frequent words"
    print words
    
    print "Writing pseudodoument..."
    write_pseudodocument(words, inputFile, outputFile)
    json.dump(dict2, codecs.open(dictFile2, 'w', encoding='utf8'), ensure_ascii=False)    
        
    
def bootstrap_basic(pseudodocInput, dictFile1, dictFile2, evaluationFile, n, k, printInfo=False):
    
    counter = 0    
    if printInfo:    
        print "Training word2vec and testing with given pseudodocument..."
    directory = pseudodocInput[:pseudodocInput.rfind("/")+1]
    word2vecFile = directory + "vec.txt"
    word2vec(["-train", pseudodocInput, "-output", word2vecFile])
    prec = test_basic(word2vecFile, dictFile1, dictFile2, evaluationFile, printInfo)
       
    while True:
        counter += 1
        
        if printInfo:
            print "Bootstraping new pseudodocument and testing performance - " + str(counter)        
        
        outputFile = pseudodocInput[:pseudodocInput.rfind(".")+1] + str(counter)
        if counter % 2 != 0:
            print "EN-IT BOOTSTRAP"
            create_pseudodocument(word2vecFile, dictFile1, dictFile2, pseudodocInput, outputFile, n, k)
        else:
            print "IT-EN BOOTSTRAP"
            create_pseudodocument(word2vecFile, dictFile2, dictFile1, pseudodocInput, outputFile, n, k)
            
        if counter > 1:
            os.remove(pseudodocInput)
        pseudodocInput = outputFile
                          
        word2vec(["-train", pseudodocInput, "-output", word2vecFile])
        precNew = test_basic(word2vecFile, dictFile1, dictFile2, evaluationFile, printInfo)
        
        if(precNew < prec):
            break
        prec = precNew
        
    # Make one final test
    if printInfo:
        test_basic(word2vecFile, dictFile1, dictFile2, evaluationFile, printInfo)
        
def create_pseudodocument_test(word2vecFile, dictFile1, dictFile2, pseudodocInput, outputFile, n, k):
    print "Started creating pseudodocument..."
    create_pseudodocument(word2vecFile, dictFile1, dictFile2, pseudodocInput, outputFile, n, k)
    print "Done"

if (__name__ == '__main__'):
#     n = mp.cpu_count()*2
#     wordNum = 30
#     k = wordNum/n
#     processes = []
#       
#     for i in xrange(n):
#         start = i*k
#         end = start + k - 1
#         processes.append(mp.Process(target=output_pseudopart, args=(i, start, end, )))
#         processes[i].start()
#       
#     for p in processes:
#         p.join()
#         
#     if end < wordNum - 1:
#         processes.append(mp.Process(target=output_pseudopart, args=(n, end + 1, wordNum, )))
#         processes[n].start()
#     words = dict()
#     words['toni'] = ['memo', 'pero', 'johnny', 'jozo']
#     inputFile = "/home/toni/Desktop/proba_input.txt"
#     outputFile = "/home/toni/Desktop/proba_output.txt"   
#     write_pseudodocument(words, inputFile, outputFile)
#     path = "toni.txt"
#     
#     #if path.rfind("/") != -1:
#     path2 = path[:path.rfind("/")+1] + "memo.txt"
#     #else:
#     #    path2 = "memo.txt"
#     print path2
    
    bootstrap_basic("Data/enit/output_200000/text_enit.txt", "Data/enit/output_200000/dict_en.txt", "Data/enit/output_200000/dict_it.txt", "Data/enit/output/dict_enit.txt", 20, 2, True)
#     word2vecFile = "Data/enit/output_200000/vec_enit.txt"
#     dictFile1 = "Data/enit/output_200000/dict_en.txt"
#     dictFile2 = "Data/enit/output_200000/dict_it.txt"
#     pseudodocInput = "Data/enit/output_200000/text_enit.txt"
#     outputFile = "Data/enit/output_200000/text_enit.1"
#     n = 4
#     k = 2
#     create_pseudodocument_test(word2vecFile, dictFile1, dictFile2, pseudodocInput, outputFile, n, k)
