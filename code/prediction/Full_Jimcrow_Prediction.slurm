#!/bin/bash
#SBATCH -A mrcs
#SBATCH --partition=gpu
#SBATCH --gres=gpu:a100:1
#SBATCH --ntasks=1
#SBATCH --time=03:00:00
#SBATCH -o slurm-%j.out
#SBATCH -e slurm-%j.err
#SBATCH --constraint=a100_80gb
#SBATCH --mem=20gb
#SBATCH --array=1-32 


OPTS1=$(sed -n "${SLURM_ARRAY_TASK_ID}"p option_1.txt)
echo $OPTS

OPTS2=$(sed -n "${SLURM_ARRAY_TASK_ID}"p option_2.txt)

echo $OPTS1
echo $OPTS2


module purge
module load apptainer tensorflow/2.13.0

apptainer run --nv $CONTAINERDIR/tensorflow-2.13.0.sif FullCorpusRun.py $SLURM_ARRAY_TASK_ID $OPTS1 $OPTS2

##Comments: The array spread out the training for each 14,000 to different systems. 
##OPTS specifies the txt file to use for indexing. Option 1 contains the beginning of the index and option 2 
##contains the end. Ours starts with 0 in option 1 and 14000 in option 2. The option files are available on the repository. 
