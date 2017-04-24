Page Rank
========

## Model
[White Paper from Brin & Page](http://infolab.stanford.edu/~backrub/google.html)
We describe the web according to the model defined by Brin & Page.
- Web = oriented graph with n nodes (pages) and branches (links)
- Web surfer = goes from nodes to nodes through links or teleportation (dumping factor)

When the web surfer is on a node "i"
    * [proba (1-d)] goes randomly on linked nodes (j_1,... j_k) through n_i outcoming links
    * [proba d] goes randomly among the n nodes

## Algorithm
**Variables**
- n : nombre de pages du web
- d : probabilité de téléportation (dumping factor) = 0.15
- n_i : nombre de liens sortants de la page i
- tol : tolerance for convergence
- (future version) memory_size : minimum node's memory size in the cluster

**Description**
- For each web surfer's move we define a step "s"
- Ps: n-column vector defining probabilities to go on a node "i" at next step
- P function is such as P = (P0,P1,...)
- At some point P converged (||P(s) - P(s-1)|| ~ 0). Then we will define Ps as pagerank for each node
- At step 0: P0 = [1/n,...,1/n]
- At step "s", Ps such as:
```
P(s) = (1-d) x T x P(s-1) + d/n x U
for a given page "i"
Pi(s) = (1-d) x Ti x P(s-1) + d/n x U
```
    * U: n-column vector - d*U = dumping probability from node i to node j
    * T: transition matrix such as T[i,j] = I[i,j]/n_j
    * G: n*n matrix of "outcoming links" - G[i,j] = 1 if i links to j 0 if not
    * I = G(-1): matrix of "incoming links" - I[i,j] = 1 if j links to i 0 if not
    * n_i: "outcoming links" number for a given node i

## Process
1. (not done yet) Launch mapper0 to distribute values per range such as they fit in memory of each node in the cluster
    * with test dataset, n < 10 000 so it's not required
2. Launch mapper/reducer through hadoop streaming for each step until convergence


## Architecture
**MAPPER**
INPUT DATA: file "inv_adj_list" on stdin with each line such as
    * <node "i">: <j1, j2... -1>
    * <key>: node "i"
    * <value>: "incoming links" j1,...
1. getting variables   
2. building  P(s-1) vector from last line in "ps.txt"
3. building outcoming_links_number from adj_list
    outcoming_links_number: # of outcoming links "nj" for each node j
4. building Tmat (T matrix) from input data
5. computing (Tmat*P_previous_step)
6. printing output data on stdout
OUTPUT DATA: on stdout with each line such as
    * <node "i">\t<Ti,j x Pj(s-1)>
    * <key>: node "i" | <value>: Ti,j x Pj(s-1)


**REDUCER**
INPUT DATA: Mapper OUTPUT DATA
1. setting variables
2. building  P(s-1) vector from last line in "ps.txt"
3. getting input value on stdin as <node "i">\t<TMat_Pvect_product>
4. computing "TMat_Pvect_vector" by summing "TMat_Pvect_product" for each node "i"
5. computing P(s) as P(s) = (1-d) x T x P(s-1) + d/n x U
6. sending output data
OUTPUT DATA:
    * if P didn't converge: Ps added in "/output/pagerank/ps.txt" as a new line
    * if P converged:
        - ordered pagerank list in "/output/pagerank/pagerank.txt"
        - top 20 highest pageranks on stdout


## Dataset
- Test from dataset "movies" (pages du web retrouvées par la requête movies)
- [Dataset Movies](http://www.cs.toronto.edu/~tsap/experiments/download/_movies.tar.Z)
- 3 files to have:
    1. "nodes" :
        - page list returned by the google query "movies"
        - 7966 pages with their ID, link and description
    2. "adj_list"
        - represents G matrix
        - each line is a list of outcoming links for a given node
        - each line as: pid: pid1 pid2 ... pidN -1
    3. "inv_adj_list"
        - represents I matrix
        - each line is a list of incoming links for a given node
        - each line as: pid: pid1 pid2 ... pidN -1

- To compute pagerank on a different webspace, simply get data in the same format, that is those 3 files.


## Instructions
**Manually**
0. Download dataset of your choice and put the 3 required files on hdfs @ /input/pagerank/
1. Start hadoop
```
$ start-dfs.sh
```
2. Set variables
```
$ cd <path_to_scripts>
$ HADOOP_HOME = <path/to/hadoop>
$ HDFS_INPUT_DIR = <path/to/hdfs/input/dir>
$ HDFS_OUTPUT_DIR = <path/to/hdfs/output/dir>
$ L_INPUT_DIR = <path/to/local/input/dir>
$ L_OUTPUT_DIR = <path/to/local/output/dir>
```
3. Execute mapper/reducer until convergence (each execution is one step)
```
hadoop jar $HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-2.7.3.jar \
        -input $HDFS_INPUT_DIR/inv_adj_list \
        -output $HDFS_OUTPUT_DIR \
        -mapper "$SCRIPT_PATH/pagerank_mapper.py $L_INPUT_DIR $L_OUTPUT_DIR"\
        -reducer "$SCRIPT_PATH/pagerank_reducer.py $L_INPUT_DIR $L_OUTPUT_DIR <dumping_factor> <tolerance>"
```

**With pagerank_launcher.py**
"pagerank_launcher.sh" is a bash script that allows you to:
    - set initial parameters
    - execute automatically mapper/reducer until convergence
```
$ ./pagerank_launcher.sh
```

## Output data
- stdout du reducer sur hdfs: $HDFS_OUTPUT_DIR/part-00000 :
    * not converged yet: nothing displayed
    * @ convergence: "P(s) converged!" will be printed
    * @ convergence: display top 20 highest pageranks
- $L_OUTPUT_DIR/ps.txt:
	* display on each line P(s) from s=1 (line 1) until last computed step
    * file is cleared when P converged
- $L_OUTPUT_DIR/pagerank.txt:
    * after convergence, display ordered list of pagerank for all nodes
    * each line as: <node #>,<node name>,(<node url>)\tPagerank[node]


## Performance


## Results
Here is the top 20 highest pageranks returned after convergence on movie dataset:
```

```

## Version
**(current verions) Version 1.0**

**(future version) Version 1.1**
- will include pagerank_laucher.py & pagerank_mapper0.py


## Contact
* e-mail: guillaume.attard@gmail.com
* Twitter: [@guillaumeattard](https://twitter.com/guillaumeattard)

Any feedback welcomed! Thanks for reading.
