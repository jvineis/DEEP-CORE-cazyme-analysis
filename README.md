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


## Now we can use anvio (https://merenlab.org/software/anvio/) to search our samples for gene sequences. 

In your
