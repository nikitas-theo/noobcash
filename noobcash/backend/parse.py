server_files = []
sum_all = 0 
num_all = 0
for name in server_files : 
    f = open(name,'r')
    block_addition_time = []
    for line in f : 
        if line.startswith('&&&'):
            block_addition_time.append(float(line.split('$')[1]))
    summ = 0
    num = 0
    for t1,t2 in zip(block_addition_time,block_addition_time[1:]):
        summ += t2-t1 
        num+=1 
    sum_all += summ
    num_all += num 
print('Average block addition time : ', sum_all/num_all)

client_files = []
sum_throuput  = 0
num_clients = 0

for name in client_files : 
    f  = open(name,'r')
    linelist = f.readlines()
    throuput = float(linelist[-1].split(':')[1])
    sum_throuput +=throuput
    num_clients+=1
print('Average Throughput (Trans)/s', throuput/num_clients)
    