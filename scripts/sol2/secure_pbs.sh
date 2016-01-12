TMP_FS="/work/d94/d94/shared/secure_sim/scratch/"
INPUT_FILE="/work/d94/d94/shared/secure-sim/options/sol2/motorBike.tar.gz.enc"
OUTPUT_FILE="./motorbike.tar.gz"

echo "Running secure submit"
NODE_LIST=`cat $PBS_NODEFILE | uniq`
echo "Allocated nodes $NODE_LIST"
NODE_COUNT=`cat $PBS_NODEFILE | uniq | wc -l`

IPS=""
for host in $NODE_LIST;
do
   IPS="$IPS `getent hosts $host | awk '{ print $1 }'`"
done

echo "Please enter public key:"
read pubkey

echo "Please enter private key:"
read privkey

echo "Starting Agent"
aprun -n 1 secure_sim start_agent $pubkey $privkey $INPUT_FILE -c $NODE_COUNT $IPS &
export AGENT_HOST=`cat $PBS_NODEFILE | uniq | sed -n '1p;'`
echo $AGENT_HOST

sleep 10
echo "Decrypting file to local scratch"
export MPICH_RANK_REORDER_METHOD=0
aprun -n $NODE_COUNT hostname
aprun -n $NODE_COUNT mkdir -p $TMP_FS
aprun -n $NODE_COUNT secure_sim decrypt $INPUT_FILE --agent_url=http://$AGENT_HOST:5000 --output $OUTPUT_FILE
wait
export MPICH_RANK_REORDER_METHOD=1

echo "Running Hydra"
aprun echo "Running..."

echo "Cleaning up scratch"
export MPICH_RANK_REORDER_METHOD=0
aprun -n $NODE_COUNT rm -rf $TMP_FS
export MPICH_RANK_REORDER_METHOD=1

echo "Release allocation"
exit