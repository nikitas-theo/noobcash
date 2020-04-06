#!/usr/bin/env python
# coding: utf-8

# In[17]:


import numpy as np
import matplotlib.pyplot as plt

N = 6
ind = np.arange(N)  # the x locations for the groups
width = 0.27       # the width of the bars

fig = plt.figure(figsize = (10,8))
ax = fig.add_subplot(111)

yvals = [2.0437,0.2822,7.6786,1.1899,13.5452,1.8002]
rects1 = ax.bar(ind, yvals, width, color='g')
zvals = [5.1099,4.8709,6.9813,0.9612,14.045,3.6006]
rects2 = ax.bar(ind+width, zvals, width, color='m')
plt.title('Throughput',fontsize = 20)
ax.set_ylabel('Throughput',fontsize = 15)
plt.xlabel('experiment setting',fontsize = 15)
ax.set_xticks(ind+width)
ax.set_xticklabels( ('c=1,d=4', 'c=1,d=5', 'c=5,d=4','c=5,d=5','c=10,d=4','c=10,d=5') )
ax.legend( (rects1[0], rects2[0]), ('5 clients', '10 clients') ,fontsize = 10)
plt.grid()
def autolabel(rects):
    for rect in rects:
        h = rect.get_height()
        ax.text(rect.get_x()+rect.get_width()/2., 1.05*h, '%d'%int(h),
                ha='center', va='bottom')

plt.savefig('Throughput.pdf')


# In[16]:


import numpy as np
import matplotlib.pyplot as plt

N = 6
ind = np.arange(N)  # the x locations for the groups
width = 0.27      # the width of the bars

fig = plt.figure(figsize = (10,8))
ax = fig.add_subplot(111)

yvals = [0.4893,3.5437,0.6511,4.2017,0.7382,5.5547]

rects1 = ax.bar(ind, yvals, width, color='y')
zvals = [0.1957,0.2053,0.7162,5.2019,0.7120,2.77773]
rects2 = ax.bar(ind+width, zvals, width, color='c')
plt.title('Average Block Time',fontsize = 20)
ax.set_ylabel('Average Block Time',fontsize = 15)
plt.xlabel('experiment setting',fontsize = 15)
ax.set_xticks(ind+width)
ax.set_xticklabels( ('c=1,d=4', 'c=1,d=5', 'c=5,d=4','c=5,d=5','c=10,d=4','c=10,d=5') )
ax.legend( (rects1[0], rects2[0]), ('5 clients', '10 clients') ,fontsize = 10)
plt.grid()
def autolabel(rects):
    for rect in rects:
        h = rect.get_height()
        ax.text(rect.get_x()+rect.get_width()/2., 1.05*h, '%d'%int(h),
                ha='center', va='bottom')

plt.savefig('Average Block Time.pdf')


# In[ ]:




