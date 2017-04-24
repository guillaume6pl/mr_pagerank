#!/usr/bin/env python
#coding: utf-8

# ----------------- pagerank_mapper.py / pagerank_reducer.py -------------------
# Goal :
#   Scripts Compute P(s) vector for one "step s".
#   Depend on P(s-1) values that are pulled from "/output/pagerank/ps.txt"
#   @ each execution, next P(s) is computed until convergence
#   @ convergence, pagerank list is returned in "/output/pagerank/pagerank.txt"
#
# Execution :
#   Written and tested using Python 2.7.13 / hadoop-streaming-2.7.3
#   Launched as :
#       hadoop jar <path_tohadoop_dir>/share/hadoop/tools/lib/hadoop-streaming-2.7.3.jar \
#	      -input /input/pagerank/inv_adj_list \
#	      -output /results/pagerank \
#	      -mapper pagerank_mapper.py -file \
#         -reducer pagerank_reducer.py

from __future__ import print_function
from __future__ import division
import sys,os
import numpy as np


'''
- setting variables
'''
# directories
input_dir = sys.argv[1]
output_dir = sys.argv[2]
# "n" : number of pages in our web space
with open(input_dir + '/inv_adj_list', "r") as f:
    n = 1 + int((f.readlines()[-1].split(':'))[0])


'''
- building  P(s-1) vector from last line in "ps.txt"
'''
if os.path.isfile(output_dir + '/ps.txt'):
	with open(output_dir + '/ps.txt', "r") as f:
		P_previous_step_data = f.readlines()[-1]
		P_previous_step = P_previous_step_data.split()
		P_previous_step = [float(x) for x in P_previous_step]
else:
    P_previous_step = [1 / n] * n # step 0


'''
- building outcoming_links_number from adj_list
outcoming_links_number: # of outcoming links "nj" for each node j
'''
outcoming_links_number = []
for line in open(input_dir + '/adj_list', "r"):
    node,outcoming_links_data = line.split(':')
    node = int(node)
    outcoming_links = outcoming_links_data.strip().split()
    outcoming_links = [int(x) for x in outcoming_links]
    del outcoming_links[-1]
    outcoming_links_number.append(len(outcoming_links))



'''
- building Tmat (T matrix) from stdin input (line in inv_adj_list)
- computing (Tmat*P_previous_step)
- printing output data on stdout
'''
Tmat = np.zeros((n,n))
TMat_Pvect_product = [1]*n # Product of T matrix with Ps vector
for line in sys.stdin:
########################## open(output_dir + "mapper_output.txt","w").close()
########################## for line in open(input_dir + 'inv_adj_list', "r"):
	# building Tmat
	node,incoming_links_data = line.split(':')
	node = int(node)
	incoming_links = incoming_links_data.strip().split()
	incoming_links = [int(x) for x in incoming_links]
	del incoming_links[-1]
	for j in range(n):
		if j in incoming_links:
			Tmat[node][j] = 1 / outcoming_links_number[j]
		else:
			Tmat[node][j] = 0
	# computing Tnode,j x P_previous_step
	TMat_Pvect_product[node] = [a * b for a, b in zip(Tmat[node], P_previous_step)]
	# OUTPUT DATA: key: node "i" | value: TMat_Pvect_product
	for TMat_Pvect_product_i in TMat_Pvect_product[node]:
		print("%i\t%f" % (node,TMat_Pvect_product_i))
		########################## with open(output_dir + "mapper_output.txt","a") as f:
		########################## 	f.write("%i\t%f" % (node,TMat_Pvect_product_i))
		########################## 	f.write('\n')
