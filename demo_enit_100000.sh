#echo "Preprocessing..."
#python preprocess.py -n 1000 -d Data/enhr/output/ Data/enhr/wikicomp-2015_hren.xml

echo "Training word2vec..."
python word2vec.py --train=Data/enit/output/text_enit.txt --output=Data/enit/output/vec_enit.txt

#echo "Creating test set..."
#python create_test.py Data/enit/output/ en it 1000

#echo "Testing..."
#python test_basic.py Data/enit/output/vec_enit.txt Data/enit/output/dict_en.txt Data/enit/output/dict_it.txt Data/enit/output/dict_enit.txt
