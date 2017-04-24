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
#	      -mapper pagerank_mapper.py \
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
# dumping factor
d = sys.argv[3]
d = float(d)
# tolerance factor
tol = sys.argv[4]
tol = float(tol)
# Product of T matrice with P(s-1) vector
TMat_Pvect_vector=[]
[1]*n
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
- getting input value on stdin as <node "i">\t<TMat_Pvect_product>
- computing "TMat_Pvect_vector" by summing "TMat_Pvect_product" for each node "i"
'''
last_node = None
last_TMat_Pvect_product = 0
for line in sys.stdin:
########################## for line in open(output_dir + 'mapper_output.txt', "r"):
	# get key/values
	node,TMat_Pvect_product = line.split('\t')
	node=int(node)
	TMat_Pvect_product = float(TMat_Pvect_product)

	# sum TMat_Pvect_product values for same node i
	if last_node is None:
		last_node = node
		last_TMat_Pvect_product = 0
	if node == last_node:
		last_TMat_Pvect_product += TMat_Pvect_product
	else:
		TMat_Pvect_vector.append(last_TMat_Pvect_product)
		# set new values
		last_node = node
		last_TMat_Pvect_product = TMat_Pvect_product

# ajout du dernier mot non traité par l'étape 1
TMat_Pvect_vector.append(last_TMat_Pvect_product)
print("=TMat_Pvect_vector=========================")
print(TMat_Pvect_vector)

'''
- computing P(s) as P(s) = (1-d) x T x P(s-1) + d/n x U
'''
Ps_temp = [x * (1-d) for x in TMat_Pvect_vector]
Ps = [x + d/n for x in Ps_temp]



'''
- sending output data
'''
Pdiff = [abs(a - b) for a, b in zip(Ps, P_previous_step)]
# if [Ps-Ps-1 > tol]: add new Ps value into "ps.txt" as a new line
if max(Pdiff) > tol:
	with open(output_dir + "/ps.txt","a") as f:
		for node_pagerank in Ps:
			f.write('%f ' % (node_pagerank))
		f.write('\n')
# if [Ps-Ps-1 < tol]
else:
	# inform about convergence
	print("\n>>>>>>>>> P(s) converged!\n\n")

	# building Pagerank as list of [<node name>,<node url>,Ps[node]]
	Pagerank = []
	Pagerank_value = Ps
	node_urls = []
	node_names = []
	line_number = 0
	for line in open(input_dir + '/nodes','r'):
		# building range for reading urls and node names
		node_urls_range = [3 + x*5 for x in range(n)]
		node_names_range = [4 + x*5 for x in range(n)]
		if line_number in node_urls_range:
			node_urls.append(line.strip())
			#print(node_urls)
		if line_number in node_names_range:
			node_names.append(line.strip())
		line_number +=1
	for node in range(n):
		Pagerank.append((node_names[node],node_urls[node],Pagerank_value[node]))
	Pagerank = sorted(Pagerank,key = lambda x: x[2] ,  reverse=True)

	# sending ordered page rank list in "pagerank.txt" such as:
	# line = <node #>,<node name>,(<node url>)\tPagerank[node]
	with open(output_dir + '/pagerank.txt','w') as f:
		for node in range (n):
			f.write("%i.%s (%s)\t%f\n" % (node,Pagerank[node][0],Pagerank[node][1],Pagerank[node][2]))
	# display top 20 highest pagerank
	print('===========================================')
	print('Top 20 highest pagerank -------------------')
	print('===========================================\n')
	rank = 1
	for (t1,t2,t3) in Pagerank[:20]:
		print(">>> #%i --------------------" % (rank))
		print(t1)
		print(t2)
		print("PR = %.5f\n\n" % (t3))
		rank +=1
