#!/bin/bash
# pagerank_launcher.sh
#
# Usage: ./pagerank_launcher.sh
# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
# set variables
# -----------------------------------------------------------------------------
HADOOP_HOME_default="$HADOOP_HOME"
SCRIPT_PATH_default=$PWD
L_INPUT_DIR_default="$SCRIPT_PATH_default/input"
L_OUTPUT_DIR_default="$SCRIPT_PATH_default/output"
HDFS_INPUT_DIR_default="/pagerank/input"
HDFS_OUTPUT_DIR_default="/pagerank/output"
d_default="0.15"
tol_default="0.01"
# hadoop_home
read -p "Enter hadoop home path (default is $HADOOP_HOME): " HADOOP_HOME
if [ $HADOOP_HOME="" ]
then
    HADOOP_HOME=$HADOOP_HOME_default
fi
# local scripts directory (default is $pwd)
read -p "Enter script path (default is $PWD): " SCRIPT_PATH
if [ $SCRIPT_PATH="" ]
then
    SCRIPT_PATH=$SCRIPT_PATH_default
fi
# local input dir (default is $script_dir/input - each folder inside is a different web space)
read -p "Enter local input dir (default is $SCRIPT_PATH/input): " L_INPUT_DIR
if [ $L_INPUT_DIR="" ]
then
    L_INPUT_DIR=$L_INPUT_DIR_default
fi
# local output dir (default is $script_dir/output)
read -p "Enter local output dir (default is $SCRIPT_PATH/output): " L_OUTPUT_DIR
if [ $L_OUTPUT_DIR="" ]
then
    L_OUTPUT_DIR=$L_OUTPUT_DIR_default
fi
# hdfs input dir (default is /pagerank/input)
read -p "Enter hdfs input dir (default is /pagerank/input - NB: build sub dir first on hdfs!): " HDFS_INPUT_DIR
if [ $HDFS_INPUT_DIR="" ]
then
    HDFS_INPUT_DIR=$HDFS_INPUT_DIR_default
fi
# hdfs output dir (default is /pagerank/output)
read -p "Enter hdfs output dir (default is /pagerank/output - NB: build sub dir first on hdfs!): " HDFS_OUTPUT_DIR
if [ $HDFS_OUTPUT_DIR="" ]
then
    HDFS_OUTPUT_DIR=$HDFS_OUTPUT_DIR_default
fi


# -----------------------------------------------------------------------------
# set parameters
# -----------------------------------------------------------------------------
# choose webspace
echo "Webspace available:"
ls $L_INPUT_DIR | xargs -n 1 basename 2> /dev/null
echo "NB: to add a webspace, build a directory inside your local input directory with the name of the webspace and containing mandatory files."
read -p "Enter the webspace of your choice: " webspace
# check if input files are valid (nodes, adj_list, inv_adj_list)
while [ ! -e $L_INPUT_DIR/$webspace/nodes ] || [ ! -e $L_INPUT_DIR/$webspace/adj_list ] || [ ! -e $L_INPUT_DIR/$webspace/inv_adj_list ]
do
    echo "webspace \"$webspace\" is not a webspace valid. Make sure it contains 3 files \"nodes\",\"adj_list\" and \"inv_adj_list\" "
    read -p "Enter the webspace of your choice: " webspace
done
    echo "webspace \"$webspace\" is a valid webspace."

# choose tolerance for convergence
read -p "Enter tolerance for convergence (default is 0.01): " tol
if [ $tol="" ]
then
    tol=$tol_default
fi
# choose dumping factor
read -p "Enter dumping factor (default is 0.15): " d
if [ $d="" ]
then
    d=$d_default
fi

# -----------------------------------------------------------------------------
# hadoop configuration
# -----------------------------------------------------------------------------
# start hadoop (option to choose)
if [ -z $"`ps -ef | grep hadoop`" ]
then
	$HADOOP_HOME/sbin/start-dfs.sh
fi
# copy input files on hdfs
$HADOOP_HOME/bin/hdfs dfs -mkdir "$HDFS_INPUT_DIR" 2> /dev/null
$HADOOP_HOME/bin/hdfs dfs -mkdir "$HDFS_INPUT_DIR/$webspace" 2> /dev/null
$HADOOP_HOME/bin/hdfs dfs -put "$L_INPUT_DIR/$webspace/* $HDFS_INPUT_DIR/$webspace" 2> /dev/null
# make output dir on hdfs
$HADOOP_HOME/bin/hdfs dfs -mkdir "$HDFS_OUTPUT_DIR" 2> /dev/null
$HADOOP_HOME/bin/hdfs dfs -mkdir "$HDFS_OUTPUT_DIR/$webspace" 2> /dev/null
$HADOOP_HOME/bin/hdfs dfs -rm "$HDFS_OUTPUT_DIR/$webspace/*" 2> /dev/null
$HADOOP_HOME/bin/hdfs dfs -rmdir "$HDFS_OUTPUT_DIR/$webspace" 2> /dev/null


# -----------------------------------------------------------------------------
# Execute mapper and reducer until convergence
# -----------------------------------------------------------------------------

# Main execution
full_local_input_dir="$L_INPUT_DIR/$webspace"
full_local_output_dir="$L_OUTPUT_DIR/$webspace"
rm $L_OUTPUT_DIR/$webspace/* 2> /dev/null
let "step = 0"
start_time=`date +%s`
 while [ ! -e $L_OUTPUT_DIR/$webspace/pagerank.txt ]
 do
 	# convergence test
 	if [ $step -ne 0 ]
     then
         echo "P did not converged yet. Moving to the next step."
     fi
     let "step += 1"
    # clean hdfs output directory
     $HADOOP_HOME/bin/hdfs dfs -rm "$HDFS_OUTPUT_DIR/$webspace/*" 2> /dev/null
     $HADOOP_HOME/bin/hdfs dfs -rmdir "$HDFS_OUTPUT_DIR/$webspace" 2> /dev/null
    echo "MAPPER/REDUCER STEP $step is running..."
	# launch mapper/reducer via hadoop streaming
    hadoop jar $HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-2.7.3.jar \
	       -input "$HDFS_INPUT_DIR/$webspace/inv_adj_list" \
           -output "$HDFS_OUTPUT_DIR/$webspace" \
           -mapper "$SCRIPT_PATH/pagerank_mapper.py $full_local_input_dir $full_local_output_dir" \
           -reducer "$SCRIPT_PATH/pagerank_reducer.py $full_local_input_dir $full_local_output_dir $d $tol"
    echo "MAPPER/REDUCER STEP $step is complete."
 done
end_time=`date +%s`

# Display end results
 echo "dumping factor was set to $dumping_factor."
 echo "Pageranks for the webspace $webspace was calculated in `expr $end_time - $start_time` sec."
 echo "P converged in $step steps with a tolerance set to $tol"
