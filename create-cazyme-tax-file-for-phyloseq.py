#!/usr/bin/env python

import sys

cdict = {}
for line in open(sys.argv[1], 'r'):
    x = line.strip().split('\t')
    cdict[x[1]] = x[0:len(x)]

# this is the file that is created by the x_run-anvio-hmm-matrix.shx script on discovery (usually called ALL-CAZY-HITS.txt)

c_hits = []

for line in open(sys.argv[2], 'r'):
    x = line.strip().split('\t')
    if x[0] == "genome_or_bin":
        for e in x:
            c_hits.append(e)

print("I found %s hits in the file containing the hmm hits to the cazy database" %len(c_hits))
        
    
outfile = open(sys.argv[3], 'w')

for element in c_hits:
    if element == "genome_or_bin":
        outfile.write("MAG"+'\t'+"group"+'\t'+"id"+'\t'+"EC"+'\t'+"function"+'\n')
    if "PL" in element and element in cdict.keys():
        outfile.write(element+'\t'+"PL"+'\t'+'\t'.join(cdict[element])+'\n')
    if "AA" in element and element in cdict.keys():
        outfile.write(element+'\t'+"AA"+'\t'+'\t'.join(cdict[element])+'\n')
    if "GH" in element and element in cdict.keys():
        outfile.write(element+'\t'+"GH"+'\t'+'\t'.join(cdict[element])+'\n')
    if "GT" in element and element in cdict.keys():
        outfile.write(element+'\t'+"GH"+'\t'+'\t'.join(cdict[element])+'\n')
    if "CE" in element and element in cdict.keys():
        outfile.write(element+'\t'+"CE"+'\t'+'\t'.join(cdict[element])+'\n')
    if "CB" in element and element in cdict.keys():
        outfile.write(element+'\t'+"CE"+'\t'+'\t'.join(cdict[element])+'\n')
    elif element not in cdict.keys():
        if "PL" in element:
            outfile.write(element+'\t'+"PL"+'\t'+"unknown"+'\t'+"unknown"+'\t'+"unknown"+'\t'+"unknown"+'\n')
        if "AA" in element:
            outfile.write(element+'\t'+"AA"+'\t'+"unknown"+'\t'+"unknown"+'\t'+"unknown"+'\t'+"unknown"+'\n')
        if "GH" in element:
            outfile.write(element+'\t'+"GH"+'\t'+"unknown"+'\t'+"unknown"+'\t'+"unknown"+'\t'+"unknown"+'\n')
        if "GT" in element:
            outfile.write(element+'\t'+"GT"+'\t'+"unknown"+'\t'+"unknown"+'\t'+"unknown"+'\t'+"unknown"+'\n')
        if "CE" in element:
            outfile.write(element+'\t'+"CE"+'\t'+"unknown"+'\t'+"unknown"+'\t'+"unknown"+'\t'+"unknown"+'\n')
        if "CB" in element:
            outfile.write(element+'\t'+"CB"+'\t'+"unknown"+'\t'+"unknown"+'\t'+"unknown"+'\t'+"unknown"+'\n')

        
        
