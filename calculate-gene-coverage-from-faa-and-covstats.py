#!/usr/bin/env python

import argparse
from Bio import SeqIO

parser = argparse.ArgumentParser(description='''This is an amazing script that will calcluate the coverage of a collection of hmm hits for a set of metagenomic samples. To do this, we multiply the average fold cov of the scaffold ( in the covstats file) by the length of the gene (in the fasta file header) and then divide this by average read lenght (150). Then we sum up the total of these reads and divide by the total number of reads used to assemble the sample (high quality reads) which gives us pretty much the best estimate of gene abundance in the sample. Its similar to creating a set of genes that are specific to a sample and then tabulating the coverage of the gene using the mapping results that were generated using bbmap to extimate the coverage of the gene. I think this is preferrable to mapping to a single set of reference genes that have nothing to do with the environment you are exploring. The downside is that you are dependent on assemlby, and if the assembly underrepresents your gene of interest, you could be in some hot watter.''')
parser.add_argument('-genes', help = 'the output from the genes called by the hmm and tabulated using anvio')
parser.add_argument('-rc', help = 'the file containing the read counts for each sample that will be used to normailize the coverage estimates')
parser.add_argument('-o', help = 'the prefix of a file name  to write a tab separated output for both the count and relative abundance estimates')
parser.add_argument('-cov', help = 'a complete path to the direcotry containing the covstats files that you generated using bbmap')
args = parser.parse_args()

outfile_rel = open(args.o+'_rel.txt', 'w') # where you will write the amazing relabundance results
outfile_rel.write("gene"+'\t')

outfile_cnt = open(args.o+'_cnt.txt', 'w') # where you will write the count results
outfile_cnt.write("gene"+'\t')

cazy_hit_dict = {}
count = 0
for seq in SeqIO.parse(open(args.genes, 'r'), "fasta"):
    gene = seq.id.split("___")[0]
    sample = seq.id.split(":")[1].split("|")[0].split("_")[1]
   # print(sample)
    scaffold = "_".join(seq.id.split(":")[4].split("_")[1:4]).split("|")[0]
    length = seq.id.split(":")[8]
    cazy_hit_dict[count] = [gene, sample, scaffold, length]
    count += 1
    
all_genes = [] # a list of genes
for key in cazy_hit_dict.keys():
    all_genes.append(cazy_hit_dict[key][0])

genes = set(all_genes)

print("I found %s genes in your data, here they are" %len(genes))
print(genes)


def collect_and_norm(sample, gene):
    count_hits = 0 # to start the count of the gene you are looking for
    hits = [] # and empty list to write the count and rel abund of the gene within a sample
    table = args.cov+sample+"-vs-"+sample+"-covstats.txt" # this might need to be edited, depending on the project.  watch out.
    table_dict = {}
    fold_cov = [] # This will hold the average fold coverage for the scaffolds that match for the gene and the sample.
    reads = read_count_dict[sample][8]
    x = open(table, 'r')
    for line in x: # create a dictionary for the covstats of the sample
        y = line.strip().split('\t')
        if "scaffold" in y[0]: # The unique scaffold id is the key
            table_dict[y[0]]=y[0:len(y)] #The average fold cov = 1, num reads would be the sum of 6 and 7, and lenght of scaffold is 
    for key in cazy_hit_dict.keys():# Look through the cazy_hit_dict for matches to the target gene and the sample
        if cazy_hit_dict[key][0] == gene and cazy_hit_dict[key][1] == sample:
            count_hits += 1 # add the observation to the count 
            gene_len = float(cazy_hit_dict[key][3]) # found in the fasta header
            read_len = float(150) # You could change this based on the sequencing run or if you trimmed the reads to a specific length
            ave_fold_cov = float(table_dict[cazy_hit_dict[key][2]][1]) #found in the covstats table
            reads_for_onex_coverage = float(gene_len/read_len) # The number of reads required for 1x coverage of the gene
            reads_for_obs_ave_coverage = float(reads_for_onex_coverage*ave_fold_cov) # The number of reads required for the observed coverage of the gene in the sample
            fold_cov.append(reads_for_obs_ave_coverage) # add this number of reads for this individual gene hit to the list.
    norm_hits = sum(fold_cov)/float(read_count_dict[sample][8])*100 # the total observed reads mapping all genes annotated to one of the cazy hmms normalized by the total number of high quality reads used for the assembly.
    print(gene,sample,norm_hits,count_hits)
    hits.append(norm_hits)
    hits.append(count_hits)
    print(hits)
    return(hits)

read_count_dict = {} # a dictionary to store each sample name and the number of genes in the assembly.. Also contains the number of total reads and reads in the assembly. Thanks JGI. 
## I commented out this part so that you can see how a change might be made to acommodate the different naming conventions used for samples across many projects.
#for line in open(args.rc, 'r'):#The number of reads in the dataset is found in field 8, reads mapped to assembly(from JGI) in field 9
#x = line.strip().split()
#if "s_" in x[0]:
#outfile_rel.write(x[0]+'\t')
#outfile_cnt.write(x[0]+'\t')
#read_count_dict[x[0]] = x[0:len(x)]
#outfile_rel.write('\n')
#outfile_cnt.write('\n')

for line in open(args.rc,'r'):
   x = line.strip().split('\t')
   if "s_" in x[0]:
       s_name = x[3]# this is the important part that I changed so the sample name in the list of samples will match the name of the covstats.txt file
       outfile_rel.write(s_name +'\t')
       outfile_cnt.write(s_name +'\t')
       read_count_dict[s_name] = x[0:len(x)]
outfile_rel.write('\n')
outfile_cnt.write('\n')


for g in genes:
    outfile_rel.write(str(g)+'\t')
    outfile_cnt.write(str(g)+'\t')
    for key in read_count_dict.keys():
        x = collect_and_norm(key, g)# use the collect_and_norm fuction to write normalized gene relative abundance to your output file.
        outfile_rel.write(str(x[0])+'\t')
        outfile_cnt.write(str(x[1])+'\t')
    outfile_rel.write('\n')
    outfile_cnt.write('\n')
