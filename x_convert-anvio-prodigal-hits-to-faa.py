#!/usr/bin/env python

import argparse
## 

parser = argparse.ArgumentParser(description='''convert the txt file output from anvi-export-gene-calls into a faa fasta file format.''')
parser.add_argument('--i', help='the resulting file from the anvi-export-gene-calls command')
parser.add_argument('--o', help='the name you want to give to your beautiful fasta format file')
args=parser.parse_args()

# Create an empty dictionay for the elements in each line of the anvi-export-gene-calls table
seq_dict = {}

# Create a empty file for your output. 
outfile = open(args.o, 'w')

for line in open(args.i, 'r'):
    x = line.strip().split('\t')
    name = '_'.join(x[0:4])
    outfile.write(">"+name+'\n'+x[9]+'\n')
    
