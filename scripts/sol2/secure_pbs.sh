export TMP_FS="~/scratch/"
export INPUT_FILE="~/secure-sim/options/sol2/motorBike.tar.gz.enc"
export OUTPUT_FILE="./motorbike.tar.gz"

echo "Running secure submit"
export NODE_LIST=`cat $PBS_NODEFILE | uniq`
echo "Allocated nodes $NODE_LIST"
export NODE_COUNT=`cat $PBS_NODEFILE | uniq | wc -l`

IPS=""
for host in $NODE_LIST;
do
   IPS="$IPS `getent hosts $host | awk '{ print $1 }'`"
done

echo $IPS

echo "Please enter public key:"
read pubkey

echo "Please enter private key:"
read privkey

echo "Starting Agent"
echo $NODE_LIST
aprun -n 1 secure_sim start_agent $pubkey $privkey $INPUT_FILE -c $NODE_COUNT $IPS &
export AGENT_HOST=`cat $PBS_NODEFILE | uniq | sed -n '1p;'`
echo $AGENT_HOST

sleep 120
echo "Decrypting file to local scratch"
#srun -m cyclic -n $NODE_COUNT hostname
#srun -m cyclic -n $NODE_COUNT mkdir -p $TMP_FS
#srun -D $TMP_FS -m cyclic -n $NODE_COUNT secure_sim decrypt $INPUT_FILE --agent_url=http://$AGENT_HOST:5000 --output $OUTPUT_FILE
wait

echo "Running Hydra"
#srun echo "Running..."
#srun -D $TMP_FS ls

echo "Cleaning up scratch"
#srun -m cyclic -n $NODE_COUNT rm -rf $TMP_FS

echo "Release allocation"
exit
