#!/bin/bash
#
#SBATCH --time=6:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mail-type=ALL
#SBATCH --partition=serc,hns,normal
#SBATCH --job-name="InVEST DOIs: artifact download"
#SBATCH --output=/scratch/users/jadoug06/slurm-logfiles/slurm-%j.%x.out

module load python/3.9.0

python3 4_download_all_artifacts.py
