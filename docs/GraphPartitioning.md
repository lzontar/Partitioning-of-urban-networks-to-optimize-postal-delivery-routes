## Graph partitioning
To partition the graphs, you need to additionally install `metis` library:
- you can find the instructions on http://glaros.dtc.umn.edu/gkhome/metis/metis/download
(if using Mac OS, you can just simply run `brew install metis`).<br>
- after installing the library you also need to install a python wrapper for metis, so we can use the functionalities
  of the library in our python code. You can install it with `pip install metis`.

After installing all the requirements, you can now run our scripts for graph partitioning:
* `clustering-utils.py` is an implementation of 7 graph partitioning algorithms. When running the script,
  you need to pass a parameter that tells the program with which graph you are working with. When the script finishes,
  it saves 7 new graphs into `data/graphs/with_communites`, where from each file name you can see with which algorithm was
  generated. The clusters to whom nodes belong are added as attribute in the graph with name `cluster_id`.
  ```shell script
  python clustering-utils.py -n tolmin
  ```
* Similarly, you can run `kmeans-clustering.py` and `kmeans-clustering-size.py`. The first script applies k-means
clustering on the graph and uses the distance information of edges, and the second one does the same, but also tries to
make final clusters the same size.
  ```shell script
  python kmeans-clustering.py -n tolmin`
  python kmeans-clustering-size.py -n tolmin`
  ```