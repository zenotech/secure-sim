TMP_FS="/scratch/ssim"
INPUT_FILE="/gpfs/thirdparty/zenotech/workarea/secure-sim/options/sol2/motorBike.tar.gz.enc" 
OUTPUT_FILE="./motorbike.tar.gz"

echo "Running secure submit"
echo "Allocated nodes $SLURM_NODELIST"
NODE_COUNT=`scontrol show hostnames $SLURM_NODELIST | wc -w`

IPS=""
for host in $SLURM_NODELIST;
do
   IPS="$IPS `getent hosts $host | awk '{ print $1 }'`"
done

echo "Please enter public key:"
read pubkey

echo "Please enter private key:"
read privkey

echo "Starting Agent"
srun -m arbitrary -w $SLURM_NODELIST -n 1 secure_sim start_agent $pubkey $privkey $INPUT_FILE -c $NODE_COUNT $IPS &
AGENT_HOST=`scontrol show hostnames $SLURM_NODELIST | sed -n '1p;'`

sleep 10

echo "Decrypting file to local scratch"
srun -m cyclic -n $NODE_COUNT hostname
srun -m cyclic -n $NODE_COUNT mkdir -p $TMP_FS
srun -D $TMP_FS -m cyclic -n $NODE_COUNT secure_sim decrypt $INPUT_FILE --agent_url=http://$AGENT_HOST:5000 --output $OUTPUT_FILE
wait

echo "Running Hydra"
srun echo "Running..."  
srun -D $TMP_FS ls

echo "Cleaning up scratch"
srun -m cyclic -n $NODE_COUNT rm -rf $TMP_FS

echo "Release allocation"
exit

