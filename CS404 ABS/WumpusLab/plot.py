import sys
import matplotlib.pyplot as plt

in_file = open(sys.argv[1],"r")
fig = plt.figure('Learning curve for file '+sys.argv[1])
rst = []

for line in in_file:
#	print line
	rst.append(float(line.split('\n')[0]))

plt.plot(range(1,len(rst)+1),rst)
plt.xlabel('episodes')
plt.ylabel('rewards')
plt.title('Learning curve for file '+sys.argv[1])
plt.grid()
plt.show()	
