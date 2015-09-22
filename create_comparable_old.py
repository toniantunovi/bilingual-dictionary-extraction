import codecs
import requests
import sys
from bs4 import BeautifulSoup

def create_comparable(lan1, lan2, lan1IndexFile, outputFile, n=None):
    
    fIn = codecs.open(lan1IndexFile, 'r', encoding='utf8') 
    fOut = codecs.open(outputFile, 'w', encoding='utf8')
    
    fOut.write("<wikipediaComparable name=\"" + lan1 + "-" + lan2 + "\">\n<header>\n</header>\n")
    count = 0
    for line in fIn:
        lline = line.lower()
        if 'wiki' in lline or '.jpg' in lline:
            continue
        
        source = line[line.rfind(':')+1:len(line)-1].replace(" ", "_")        
        url = "http://www.wikidata.org/w/api.php?action=wbgetentities&sites=" + lan1 + "wiki&titles=" + source + "&languages=" + lan2 + "&props=labels&format=json"
        r = requests.get(url);
        
#         print str(count) + str(r.json())
        index, = r.json().values()[0]
        res_type = r.json().values()[0].values()[0].values()[0]
        if index != '-1' and res_type != 'item':
            count += 1
            url1 = "http://" + lan1 + ".wikipedia.org/w/api.php?action=parse&page=" + source + "&format=xml"
            r1 = requests.get(url1)
            html1 = BeautifulSoup(r1.text).api.parse
            if not html1:
                continue
            else:
                html1 = html1.text            
            article1 = ' '.join([ p.getText() for p in BeautifulSoup(html1).findAll("p")])
            
            target = r.json()['entities'].values()[0]['labels'][lan2]['value'].replace(" ", "_")            
            url2 = "http://" + lan2 + ".wikipedia.org/w/api.php?action=parse&page=" + target + "&format=xml"
            r2 = requests.get(url2)
                        
            html2 = BeautifulSoup(r2.text).api.parse
            if not html2:
                continue
            else:
                html2 = html2.text
            article2 = ' '.join([ p.getText() for p in BeautifulSoup(html2).findAll("p")])
            
            fOut.write("<articlePair id=\"" + str(count) + "\">\n")
            fOut.write("<article lang=\"" + lan1 + "\" name=\"" + source.replace("_"," ") + "\">\n")
            fOut.write("<categories name=\"\"/>\n")
            fOut.write("<content>\n" + article1 + "\n</content>\n</article>\n")
            
            fOut.write("<article lang=\"" + lan2 + "\" name=\"" + target.replace("_"," ") + "\">\n")
            fOut.write("<categories name=\"\"/>\n")
            fOut.write("<content>\n" + article2 + "\n</content>\n</article>\n")
            
            fOut.write("</articlePair>\n")
            
            if n is not None and count == n:
                break
            
            if count % 10 == 0:
                print count
            
    fOut.write("</wikipediaComparable>")
    fOut.close()
        
def main(sys_argv):
    create_comparable("hr", "en", "Data/hren/hrwiki-20150316-pages-articles-multistream-index.txt", "Data/hren/wikicomp-2015_200000_hren.xml", 200000)

if __name__ == "__main__":
    main(sys.argv)
    
            
        
