# DEEP-CORE-cazyme-analysis
Analysis of short metagenomic sequencing reads for carbohydrate utilization

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
    conda env create -f anvio-environment.yml
    conda env create -f 

## Now we are ready to annotate the assembled contigs reconstructed by JGI for genes related to carbohydrate use in the CAZyme database.


http://bcb.unl.edu/dbCAN2/download/Databases/

You will need the "tools" directory, stp.hmm, tf-1.hmm, tf-2.hmm

The directions for handling running the search can be found in the readme file within this directory.
http://bcb.unl.edu/dbCAN2/download/Databases/dbCAN-old@UGA/

The steps to call the cazymes begins with gene calling for each of your genome bins (something like this)
for i in `cat samples.txt `; do prodigal -i $i'-contigs.fa' -p meta -a $i'-contigs.faa'; done

Then run the hmm search against the cazyme database
for i in `cat samples.txt `; do hmmscan --domtblout $i'-out.dm' /Users/joevineis/scripts/databas/dbCAN2/dbCAN-HMMdb-V7.txt $i'-contigs.faa' > $i'-cazy.out'; done

Then parse the output and filter for quality hits only 
for i in `cat samples.txt `; do python /Users/joevineis/scripts/databas/dbCAN2/tools/hmmscan-parser $i'-out.dm' > $i'.out.dm.ps' ; done
for i in `cat samples.txt `; do cat $i'.out.dm.ps' | awk '$5<1e-15&&$10>0.35' > $i'-cazy-stringent-hits.txt'; done

Then you can use the script attached to combine multiple genomes into a single presence absence table of hits. Something like this... where "samples.txt" is a text file containing a single column of genome names.. 
python combine-cazy-tables.py samples.txt


## Now we can create our contig databases and use anvio (https://merenlab.org/software/anvio/) to identify genes in our samples and prepare them for comparison with the CAZY database

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
    
and in the third line applys 'x_convert-anvio-prodigal-hits-to-faa.py' to the text output files and converts them to faa files so that their format is friendly for comparison with the CAZY database. Sumbit the bash script with all of these lines using the command:

    sbatch x_run-CAZY.shx

Once this has finished running, we will start a new session and activate the hmmer tool using: 

    conda activate hmmer
    
and add the following code to use hmmer, running the script with all other lines except the following commented out. Hmmer is a tool used for sequence alignments

    hmmscan --domtblout x_ANVIO-assembly-dbs/s_${SAMPLE}-cazy-out.dm /work/jennifer.bowen/DBs/CAZY/dbCAN-fam-HMMs.txt x_ANVIO-assembly-dbs/s_${SAMPLE}-prodigal.faa > x_ANVIO-assembly-dbs/s_${SAMPLE}-cazy.out
