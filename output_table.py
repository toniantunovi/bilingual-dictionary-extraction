import re
import sys

def usage(error):
    print "Create Latex tables from output of tests."
    exit(error)
    
paramsBasic = ["d=50, cs=5",  
"d=50, cs=16",
"d=50, cs=48",  
"d=100, cs=5",  
"d=100, cs=16",
"d=100, cs=48",
"d=150, cs=5", 
"d=150, cs=16",
"d=150, cs=48",
"d=200, cs=5",     
"d=200, cs=16",
"d=200, cs=48",
"d=250, cs=5",  
"d=250, cs=16", 
"d=250, cs=48", 
"d=300, cs=5",  
"d=300, cs=16",
"d=300, cs=48"]

paramsBootstrap = ["n=0, k=0",
          "n=100, k=5",
          "n=100, k=10",
          "n=1000, k=5",
          "n=1000, k=10"]

params = ["n=0, p=0",       # params - mikolov
          "n=1000, p=0.7",
          "n=1000, p=0.8",
          "n=1000, p=0.9",
          "n=5000, p=0.7",
          "n=5000, p=0.8",
          "n=5000, p=0.9",
          "n=7000, p=0.7",
          "n=7000, p=0.8",
          "n=7000, p=0.9"]

def output_table(fileIn1, fileIn2, fileOut, cbow):    
    input1 = open(fileIn1, 'r')
    input2 = open(fileIn2, 'r')
    output = open(fileOut, 'w') 
    n = len(params)
    
    counter = 0
    cbow = cbow == "cbow"
    if cbow: 
        start = False
    else:
        start = True
    
    outStr = []
    for line in input1:
        if len(re.findall(r'\d+\.\d+', line) ) == 3:
            prec = re.findall(r'\d+\.\d+', line)
            
            if start:
                outStr.append(params[counter%n] + " ")
                outStr[len(outStr)-1] += "& " + (prec[0][0:5] if len(prec[0]) > 4 else prec[0]) + " & " + (prec[1][0:5] if len(prec[1]) > 4 else prec[1]) + " & " + (prec[2][0:5] if len(prec[2]) > 4 else prec[2]) + " & "
                
            counter += 1
            if start and counter == n:
                break
            if not start and counter == n:
                start = True    
        
    if cbow: 
        start = False
    else:
        start = True
    
    counter = 0
    for line in input2:
      if len(re.findall(r'\d+\.\d+', line) ) == 3:
          prec = re.findall(r'\d+\.\d+', line)
          
          if start:
              outStr[counter%n] += (prec[0][0:5] if len(prec[0]) > 4 else prec[0]) + " & " + prec[1][0:5] + " & " + prec[2][0:5] + " \\\\ \n"
              
          counter += 1
          if start and counter == n:
              break        
          if not start and counter == n:
              start = True
                  
    for line in outStr:
        output.write(line)
    
    file.close(input1)
    file.close(input2)
    file.close(output)

def main(sys_argv):
    
    if len(sys_argv) == 5:
        fileIn1 = sys_argv[1]
        fileIn2 = sys_argv[2]
        fileOut = sys_argv[3]
        cbow = sys_argv[4]
        
        output_table(fileIn1, fileIn2, fileOut, cbow)     
    else:
        print "Invalid number of arguments"
        usage(1)

if __name__ == '__main__':
    main(sys.argv)