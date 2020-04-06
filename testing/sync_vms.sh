echo "Every vm (including master) will be synced"
git pull
scp {state.py,transaction.py,broadcast.py,server.py,cli.py} user@m2:/home/user/
scp {state.py,transaction.py,broadcast.py,server.py,cli.py} user@m3:/home/user/
scp {state.py,transaction.py,broadcast.py,server.py,cli.py} user@m4:/home/user/
scp {state.py,transaction.py,broadcast.py,server.py,cli.py} user@m5:/home/user/
ssh user@m2 "cp -rf {state.py,transaction.py,broadcast.py,server.py,cli.py} code/ && rm -rf {state.py,transaction.py,broadcast.py,server.py,cli.py}"
ssh user@m3 "cp -rf {state.py,transaction.py,broadcast.py,server.py,cli.py} code/ && rm -rf {state.py,transaction.py,broadcast.py,server.py,cli.py}"
ssh user@m4 "cp -rf {state.py,transaction.py,broadcast.py,server.py,cli.py} code/ && rm -rf {state.py,transaction.py,broadcast.py,server.py,cli.py}"
ssh user@m5 "cp -rf {state.py,transaction.py,broadcast.py,server.py,cli.py} code/ && rm -rf {state.py,transaction.py,broadcast.py,server.py,cli.py}"