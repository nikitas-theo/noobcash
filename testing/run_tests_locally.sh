mkdir logs 
DIR=../noobcash/
./kill_all_tests_locally.sh

nohup python ./$DIR/server.py localhost 1234 > ./logs/server_log1 & 
nohup python ./$DIR/server.py localhost 1235 > ./logs/server_log2 &
nohup python ./$DIR/server.py localhost 1236 > ./logs/server_log3 &
nohup python ./$DIR/server.py localhost 1237 > ./logs/server_log4 &
nohup python ./$DIR/server.py localhost 1238 > ./logs/server_log5 &

sleep 2

nohup python ./$DIR/cli.py localhost 1234 -n 5 -test 5 -difficulty 4 -capacity 1  > ./logs/client_log1 &
echo $! > save_pid.txt
sleep 5
nohup python ./$DIR/cli.py localhost 1235 -test 5 -difficulty 4 -capacity 1 -ch localhost -cp 1234 > ./logs/client_log2 &
echo $! > save_pid.txt
nohup python ./$DIR/cli.py localhost 1236 -test 5 -difficulty 4 -capacity 1 -ch localhost -cp 1234 > ./logs/client_log3 &
echo $! > save_pid.txt
nohup python ./$DIR/cli.py localhost 1237 -test 5 -difficulty 4 -capacity 1 -ch localhost -cp 1234 > ./logs/client_log4 &
echo $! > save_pid.txt
nohup python ./$DIR/cli.py localhost 1238 -test 5 -difficulty 4 -capacity 1 -ch localhost -cp 1234 > ./logs/client_log5 &
echo $! > save_pid.txt
