#Automatic generation of bilingual dictionaries based on semantic vector spaces

Dictionaries and phrase tables are the basis of modern statistical machine translation
systems. Traditional methods for automatic generation of bilingual dictionaries
depend on parallel bilingual corpora. Since parallel corpora is hard to acquire, newer
methods only require comparable corpora in order to work. This paper develops a method
that can automate the process of generating and extending dictionaries and phrase
tables in an unsupervised way from comparable corpora.

##Requires python 2.7 and:

sudo apt-get install python python-dev 

sudo pip install beautifulsoup4
sudo pip install numpy
sudo pip install nltk
sudo pip install goslate

TreeTagger and it's Python wrapper are also requiered- http://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger/

sudo python ~/tree-tagger/setup.py install

