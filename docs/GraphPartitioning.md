## Graph partitioning
To partition the graphs, you need to install additional libraries.

First install metis library. You can find the instructions on http://glaros.dtc.umn.edu/gkhome/metis/metis/download (if using Mac OS, you can just simply run `brew install metis`).<br>
After installing the library we also need to install a python wrapper for metis, so we can use the functionalities of the libriray in our python code. You can install it with `pip install metis`.

After installing all the requirements, we can nov run our scripts for graph partitioning:
* `python clustering-utils.py -n tolmin`
* `python kmeans-clustering.py -n tolmin`
* `python kmeans-clustering-size.py -n tolmin`

Short description of scripts:
In script `clustering-utils.py` there is an implementation of 7 graph partitioning algorithms. When running the script, we need to pass a parameter that tells the program with which graph we are working with. When the script finishes, it saves 7 new graphs into `data/graphs/with_communites`, where from each file name we can see with which algorithm was generated. The clusters to whom nodes belong are added as attribute in the graph with name `cluster_id`.