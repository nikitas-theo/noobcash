for PORT_NUMBER in 1234 1235 1236 1237 1238
do
    fuser -n tcp -k ${PORT_NUMBER}
    echo ${PORT_NUMBER}
done
kill -9 `cat save_pid.txt`
rm save_pid.txt