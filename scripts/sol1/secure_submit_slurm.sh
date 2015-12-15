#!/bin/bash
#SBATCH -p westmere
#SBATCH -A secwork
#SBATCH -n 6
#SBATCH --time=00:30:00
#SBATCH --error=job.%J.err 
#SBATCH --output=job.%J.out
#SBATCH --exclusive
export TMP_FS="/scratch/ssim"

echo "Running secure submit"
echo "Allocated nodes $SLURM_NODELIST"
export NODE_COUNT=`scontrol show hostnames $SLURM_NODELIST | wc -w`

echo "Decrypting file to local scratch"
mkdir -p $TMP_FS
srun -m cyclic -n $NODE_COUNT mkdir -p $TMP_FS
cd $TMP_FS
srun -m cyclic -n $NODE_COUNT secure_sim decrypt --key_module poc.external.secure /gpfs/thirdparty/zenotech/workarea/secure-sim/options/sol1/motorBike.tar.gz.enc --output ./motorbike.tar.gz 
wait

echo "Running Hydra"
srun echo "Running,,,"  
srun ls $TMP_FS

echo "Cleaning up scratch"
srun -m cyclic -n $NODE_COUNT rm -rf $TMP_FS

echo "Secure submit complete"
