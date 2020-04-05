mkdir logs 
fuser -n tcp -k 1234
kill -9 `cat save_pid.txt`

nohup ./kill_all_tests.sh

nohup python3 server.py 192.168.1.1 1234 > ./logs/server_log1 &
nohup ssh user@m2 "cd code && ./client_test.sh" &
nohup ssh user@m3 "cd code && ./client_test.sh" &
nohup ssh user@m4 "cd code && ./client_test.sh" &
nohup ssh user@m5 "cd code && ./client_test.sh" &

sleep 1

nohup python3 cli.py 192.168.1.1 1234 -n 5 -test 5 -difficulty 5 -capacity 5  > ./logs/client_log1 &
echo $! > save_pid.txt

