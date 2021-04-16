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

For this part we need to make sure we have the text file with sample names 'x_sample-names.txt' ini our working directory, so that we can apply the code in our bash file 'x_run-CAZY.shx' to all of the samples. In your working directory you should also create a new directory called "assembly-dbs"

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
    anvi-run-hmms -c s_${SAMPLE}.db -H /work/jennifer.bowen/DBs/anvio_cazy -T 40
    
#### note that you can run an individual sample if you like by commenting out the "SAMPLE" line and swapping it with "SAMPLE=targetsample". This is useful if you want to add a sample to the analysis or if something goes wrong during the hmm run. The 
