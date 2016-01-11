#!/bin/bash
#PBS -A d94
#PBS -q short
#PBS -l select=3
#PBS -l walltime=00:20:00

TMP_FS="/work/d94/d94/shared/secure_sim/scratch"
INPUT_FILE="/work/d94/d94/shared/secure_sim/data/motorBike.tar.gz.enc"
OUTPUT_FILE="./motorbike.tar.gz"
NODE_COUNT=3

echo "Running secure submit"
echo "Decrypting file to local scratch"
mkdir -p $TMP_FS
cd $TMP_FS
aprun -N 1 -n $NODE_COUNT hostname
aprun -N 1 -n $NODE_COUNT mkdir -p $TMP_FS
cd $TMP_FS
aprun -N 1 -n $NODE_COUNT secure_sim decrypt --key_module poc.external.secure $INPUT_FILE --output $OUTPUT_FILE
wait

echo "Running Hydra"
aprun echo "Running,,,"
aprun ls $TMP_FS

echo "Cleaning up scratch"
aprun -N 1 -n $NODE_COUNT rm -rf $TMP_FS

echo "Secure submit complete"
