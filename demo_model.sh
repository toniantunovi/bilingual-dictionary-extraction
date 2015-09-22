echo "Training word2vec with pseudodocument(english and italian)..."
python word2vec.py --train=Data/enit/output/text_enit.txt --output=Data/enit/output/vec_enit.txt --window=48 --size=300

echo "\nTesting basic performance"
python test_basic.py Data/enit/output/vec_enit.txt Data/enit/output/dict_en.txt Data/enit/output/dict_it.txt Data/enit/output/test_set.txt

echo "\nTraining word2vec with english text..."
python word2vec.py --train=Data/enit/output/text_en.txt --output=Data/enit/output/vec_en.txt

echo "\nTraining word2vec with italian text..."
python word2vec.py --train=Data/enit/output/text_it.txt --output=Data/enit/output/vec_it.txt

echo "\nCreating training set for translation matrix training..."
python create_training_set.py Data/enit/output/vec_enit.txt Data/enit/output/dict_en.txt Data/enit/output/dict_it.txt Data/enit/output/training_set.txt 5000 0

echo "Training tm..."
python train_tm.py -o Data/enit/output/tm Data/enit/output/test_set.txt Data/enit/output/vec_en.txt Data/enit/output/vec_it.txt

echo "Testing tm..."
python test_tm.py Data/enit/output/tm.txt Data/enit/output/test_set.txt Data/enit/output/vec_en.txt Data/enit/output/vec_it.txt Data/enit/output/dict_en.txt Data/enit/output/dict_it.txt

