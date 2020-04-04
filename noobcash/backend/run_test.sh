mkdir logs 
<<<<<<< HEAD
fuser -n tcp -k 1234
kill -9 `cat save_pid.txt`

=======
./kill_all_tests.sh
>>>>>>> 56311d24152a656d6f7feadf4781ecb3b67326ae

nohup python3 server.py 192.168.1.1 1234 > ./logs/server_log1 &
nohup ssh user@m2 "cd code && ./client_test.sh" &
nohup ssh user@m3 "cd code && ./client_test.sh" &
nohup ssh user@m4 "cd code && ./client_test.sh" &
nohup ssh user@m5 "cd code && ./client_test.sh" &

<<<<<<< HEAD
sleep 1

nohup python3 cli.py 192.168.1.1 1234 -n 5 -test 5 -difficulty 5 -capacity 5  > ./logs/client_log1 &
echo $! > save_pid.txt

=======
sleep 2

nohup python cli.py localhost 1234 -n 5 -test 5 -difficulty 2 -capacity 5  > ./logs/client_log1 &
echo $! > save_pid.txt
sleep 5
nohup python cli.py localhost 1235 -test 5 -difficulty 2 -capacity 5 -ch localhost -cp 1234 > ./logs/client_log2 &
echo $! > save_pid.txt
nohup python cli.py localhost 1236 -test 5 -difficulty 2 -capacity 5 -ch localhost -cp 1234 > ./logs/client_log3 &
echo $! > save_pid.txt
nohup python cli.py localhost 1237 -test 5 -difficulty 2 -capacity 5 -ch localhost -cp 1234 > ./logs/client_log4 &
echo $! > save_pid.txt
nohup python cli.py localhost 1238 -test 5 -difficulty 2 -capacity 5 -ch localhost -cp 1234 > ./logs/client_log5 &
echo $! > save_pid.txt
>>>>>>> 56311d24152a656d6f7feadf4781ecb3b67326ae
