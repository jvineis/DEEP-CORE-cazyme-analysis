# DEEP-CORE-cazyme-analysis
Analysis of short metagenomic sequencing reads for carbohydrate utilization

## We will be uploading files to the remote server during this project using 'scp', 'rsync', or 'wget', while in the directory you want the transer the file to.

    wget 'url'
    scp 'local file location' 'remote server address'
    rsync {NOT SURE}
    
scp and rsync (i think?) may also be used to securely copy files from the server to your local computer.

## First, we need to create an environment that contains all of the correct versions of the software that we want to use. We will use a conda environment to accomplish this. Here is the best way to get conda installed in your home environment.

    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh
    bash ~/miniconda.sh -b -p $HOME/miniconda3/
    source ~/miniconda3/bin/activate
    conda update -n base -c defaults conda
    
## Now we need to install a version of hmmer.  Use the hmmer-environment.yml file contained in this repository to run the following command. As a note.. This file was created from Joe's home directory on discovery using the first two lines below

#### For Joe

    conda activate hmmer
    conda env export > hmmer-environment.yml

#### For User

    conda env create -f hmmer-environment.yml

### If this didn't work for you.. you may need to try it this way which will download anaconda (instead of miniconda).

#### 1. Login into an interactive node:

    srun -p short -N 1 -n 16 --pty /bin/bash

#### 2. Download & install anaconda3 (similar to miniconda3):

    wget https://repo.anaconda.com/archive/Anaconda3-2020.11-Linux-x86_64.sh
    bash Anaconda3-2020.11-Linux-x86_64.sh

#### 3. Follow the prompt as before, and specify your home directory in the default location: for example: (/home/w.williamson/anaconda3).

#### 4. Source activate and update:
     
    source ~/anaconda3/bin/activate
    conda update conda -y

#### 5. Install the new environment (please note I commented out the last line in the file, it is not needed):

    conda env create -f hmmer-environment.yml

## We need to install a few more pieces of software to make this work. Lets cross our fingers and hope all goes smoothly.

#### Enter each of the commands below one at a time and follow any prompts. YOU ONLY NEED TO ACTIVATE ANACONDA IF YOU INSTALLED IT ABOVE! Otherwise, you can skip that step. The anvio-environment.yml file is located in the home directory of this git.

    srun -p short -N 1 -n 16 --pty /bin/bash
    source ~/anaconda3/bin/activate
    conda update conda -y
    conda env create -f anvio-6.2-environment.yml
    conda env create -f 

###### need to create an env for anvi 7.0
## Now we are ready to annotate the assembled contigs reconstructed by JGI for genes related to carbohydrate use in the CAZyme database

## Create our contig databases and use anvio (https://merenlab.org/software/anvio/) to identify genes in our samples and prepare them for comparison with the CAZY database

For this part we need to make sure we have the text file with sample names 'x_sample-names.txt' ini our working directory, so that we can apply the code in our bash file 'x_run-CAZY.shx' to all of the samples. In your working directory you should also create a new directory called "assembly-dbs". You only need to run the first line of the x_run-CAZY.shx script which will create the anvio database.  The rest of the steps are now antiquated.. but they could be used for methodological comparisons if you desire.  

To begin your anvio session, use:

    conda activate anvio-6.2

View and edit the bash file by using the command:

    emacs x_run-CAZY.shx

This file can be run using the command 

    sbatch x_run-CAZY.shx
    
which creates anvio databases using the first line by taking fasta files and turning them into .db files

    anvi-gen-contigs-database -f /work/jennifer.bowen/JOE/DEEP-CORE-GLOBUS-DOWNLOAD/${SAMPLE}/QC_and_Genome_Assembly/final.contigs.fasta -o assembly-dbs/s_${SAMPLE}.db

applys anvio in the second line and creates text file output with genes that have been identified in the contigs (hits)

    anvi-export-gene-calls -c assembly-dbs/s_${SAMPLE}.db -o assembly-dbs/s_${SAMPLE}-prodigal.txt --gene-caller prodigal
    
and in the third line applys 'x_convert-anvio-prodigal-hits-to-faa.py' to the text output files and converts them to faa files so that their format is friendly for comparison with the CAZY database. 

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
    outfile.write(">"+name+'\n'+x[8]+'\n')

Sumbit the bash script with all of these lines using the command:

    sbatch x_run-CAZY.shx

you can check the status of your jobs using the "squeue" command. See example below. 
 
    squeue | grep username

Once this has finished running, we will start a new session and activate the hmmer tool using:  

    conda deactivate
    conda activate hmmer
    
Uncomment the following code to use hmmer, running the script with all other lines except the following commented out. Hmmer is a tool used for sequence alignments

    hmmscan --domtblout x_ANVIO-assembly-dbs/s_${SAMPLE}-cazy-out.dm /work/jennifer.bowen/DBs/CAZY/dbCAN-fam-HMMs.txt x_ANVIO-assembly-dbs/s_${SAMPLE}-prodigal.faa > x_ANVIO-assembly-dbs/s_${SAMPLE}-cazy.out
    

### OK.  Strong work getting through that process! Now we are going to use a different approach to identify the cazy genes within each of our scaffolds. This process will use the anvio db that you created for each of your samples and run the cazy hmms using the anvi-run-hmms tool.  This will import the scaffold id, start and stop of the hit, and sequence for each of the hits to the cazy genes (if they are present in the assembly). Here is the script that we use to run this analysis. 

    #!/bin/bash
    #
    #SBATCH --nodes=1
    #SBATCH --tasks-per-node=20
    #SBATCH --mem=100Gb
    #SBATCH --time=10:00:00
    #SBATCH --partition=short
    #SBATCH --array=1-62
    SAMPLE=$(sed -n "$SLURM_ARRAY_TASK_ID"p x_sample-names.txt)
    #SAMPLE=10WP15_MG
    anvi-run-hmms -c s_${SAMPLE}.db -H /work/jennifer.bowen/DBs/anvio_cazy -T 40 --just-do-it
    
#### note that you can run an individual sample if you like by commenting out the "SAMPLE" line and swapping it with "SAMPLE=targetsample". This is useful if you want to add a sample to the analysis or if something goes wrong during the hmm run. There is no output produced by this script. The information generated by this step ends up in the anvio database, so it can be helpful to take a look into the slurm output to ensure that there were no errors.

### Create a matrix of the hmm hits for each sample using the "x_run-anvio-hmm-matrix.shx" found in this repository.  We want to know how many hits there are for each gene in each sample.  To create this matrix, we just need to run the following bash script. 

    #!/bin/bash
    #
    #SBATCH --nodes=1
    #SBATCH --tasks-per-node=10
    #SBATCH --mem=100Gb
    #SBATCH --time=05:00:00
    #SBATCH --partition=short
    anvi-script-gen-hmm-hits-matrix-across-genomes -e x-external-genomes.txt --hmm-source anvio_cazy -o x_ANVIO-cazyme.txt

#### This script requires the x-external-genomes.txt file.  Here are the steps to create this file. Run these command in the directory where you have your anvio db files. 

    ls *.db | sed 's/.db//g' > 1
    ls *.db > 2
    paste 1 2 > x-external-genomes.txt
    rm 1 2
    
#### now use emacs to add a header so that the top of the x-external-genomes.txt file looks like this. The header "name" and "contigs_db_path" must look exactly like this

    name	contigs_db_path
    s_10CB15_MG	s_10CB15_MG.db
    s_10CB15_MT	s_10CB15_MT.db
    s_10CP15_MG	s_10CP15_MG.db
    s_10CP15_MT	s_10CP15_MT.db
    s_10CT5_MG	s_10CT5_MG.db
    s_10CT5_MT	s_10CT5_MT.db
    s_10NB15_MT	s_10NB15_MT.db
    
    
#### Now run the script above that will create the matrix.

    sbatch x_run-anvio-hmm-matrix.shx
    
### Lets have a look at the resulting matrix using R so that we can see how the carbohydrate usage genes are distributed among samples. It will be helpful to have some meta data when looking at things in R.. Just so happens that I have placed a metadata file in this git repository that contains a lot of useful information about each of the samples "DEEP-CORE-METADATA.txt". Below are the lines that you need to generate a cazyme (taxonomy) file and run phyloseq exploratory analysis in R .. I find this to be truly enjoyable!

#### If you don't have phyloseq installed, now would be a great time to install.. you can read about that here https://joey711.github.io/phyloseq/install.html

#### In a terminal session on your own computer, make a directory where you will keep all of your cazyme analysis and use rsync or scp to download the x_ANVIO-cazyme.txt file created by the x_run-anvio-hmm-matrix.shx script above. The script below will produce a cazyme (taxonomy) file required by phyloseq. You will find the files required to run this script in this git repo (create-cazyme-tax-file-for-phyloseq.py and CAZyDB-ec-info.txt.07-20-2017). The second argument is the fie created by the x_run-anvio-hmm-matrix.shx -- usually called x_ANVIO-cazyme.txt and the third argument is the name of the file that you want to use for your output cazyme(taxonomy) file.  

    python create-cazyme-tax-file-for-phyloseq.py CAZyDB-ec-info.txt.07-20-2017 x_ANVIO-cazyme.txt x_ANVIO-cazyme-tax.txt
    
#### Now we need a metadata file that has details of each sample including the number of reads that went into the assembly so that we can normalize our hmm hit counts based on the number of reads available.  We need to think carefully about how to normalize.  Its possible that normalizing based on relative counts of each cazyme to the total number of cazyme hits is what we are after.. However, this doesn't normalize for the number of reads available to assemble, or the number of scaffolds in the assembly. This is an open discussion. For now we will just go with relative counts of each hmm to the total hmm hits and we can accomplish this with phyloseq.  

#### I have placed the metadata file that you need in this git repo.. Move this file (DEEP-CORE-sample-metadata.txt) into the directory that contains the x_ANVIO-cazyme.txt and x_ANVIO-cazyme-tax.txt files.  Then change the paths in the R code below and run each line to create a phyloseq object. 

    library(vegan)
    library("phyloseq")
    library("ape")
    
    # change the paths below to reflect where your files are
    # the matrix of anvio hmm hits
    mat_dc = read.table("/your/cazy/path/x_ANVIO-cazyme.txt", header = TRUE, sep = "\t", row.names = 1)
    # the cazyme (taxonomy) file that you created above
    tax_dc = read.table("/your/cazy/path/x_ANVIO-cazyme-tax.txt", header = TRUE, sep = "\t", row.names = 1)
    # the metadata file that I created for you ""
    meta_dc = read.table("/your/cazy/path/DEEP-CORE-sample-metadata.txt", header = TRUE, sep = "\t", row.names = 1)

    mat_dc = as.matrix(t(mat_dc))
    tax_dc = as.matrix(tax_dc)

    OTU = otu_table(mat_dc, taxa_are_rows = TRUE)
    TAX = tax_table(tax_dc)
    META = sample_data(meta_dc)

    dc_physeq = phyloseq(OTU,TAX,META)

#### After some discussion, we have decided to try another normalization method which will yield the true relative abundance, described below. We plan to carry out analysis with both normalization methods and compare results, but believe that this updated method will be more rigorous.

#### We used the following bash script to conduct this normalization, which outputs two text files: one with raw counts and the other with normalized counts. 

    #!/bin/bash
    #
    #SBATCH --nodes=1
    #SBATCH --time=24:00:00
    #SBATCH --tasks-per-node=10
    #SBATCH --partition=short
    #SBATCH --mem=100Gb

    python calculate-gene-coverage-from-faa-and-covstats.py -genes x_ALL-ANVIO-CAZY.faa -rc DEEP-CORE-METADATA-EXT.txt -o x_ALL-NORMALIZED-GENE-MATRIX.txt -cov /work/jennifer.bowen/JOE/DEEP-CORE/MAPPING/

#### The python script used here takes both a FASTA file containing protein information from every CAZY hit found in our sample (x_ALL-ANVIO-CAZY.faa), our sample metadata (DEEP-CORE-METADATA.txt) and a list of sample names (x_ALL-NORMALIZED-GENE-MATRIX.txt). It also uses the coverage files which contain information about samples mapped onto themselves, including average coverage, length, and GC content. 

#### For both normalization methods, we use the RStudio package phyloseq to conduct analysis and create plots, alongside anvio plots
