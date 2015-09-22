import codecs

def count_articles(fileIn):
    with codecs.open(fileIn, 'r', encoding='utf8') as fIn:
        flag = 0
        counter = 0
        for line in fIn:
            if "<content>" in line and flag == 0:
                flag = 1
            elif "</content>" in line and flag == 1:
                flag = 2
            elif "<content>" in line and flag == 2:
                flag = 3    
            elif "</content>" in line and flag == 3:                  
                counter += 1
                flag = 0
    
        return counter
    
        
if __name__ == '__main__':
    print count_articles("Data/enhr/wikicomp-2015_hren.xml")
