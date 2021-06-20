# Partitioning of urban networks to optimize postal delivery routes

## Network structure
Here, we present the structure of our network, which will represent the city road infrastructure.

**Nodes** will represent crossroads. Each node will contain information about:
* its GPS coordinates: longitude and latitude,
* a list of nearby houses to which this crossroad is the closest crossroad.

**Edges** represent connections or combination of roads between two crossroads. 
Each edge is weighted by distance (in km) and time needed to get from one crossroad to another.
 
 
##### Fetch crossroads
```
<!-- Only select the type of ways you are interested in -->
<query type="way" into="relevant_ways">
  <has-kv k="highway"/>
  <has-kv k="highway" modv="not" regv="footway|cycleway|path|service|track"/>
  <bbox-query {{bbox}}/>
</query>

<!-- Now find all intersection nodes for each way independently -->
<foreach from="relevant_ways" into="this_way">  

  <!-- Get all ways which are linked to this way -->
  <recurse from="this_way" type="way-node" into="this_ways_nodes"/>
  <recurse from="this_ways_nodes" type="node-way" into="linked_ways"/>
  <!-- Again, only select the ways you are interested in, see beginning -->
  <query type="way" into="linked_ways">
    <item set="linked_ways"/>
    <has-kv k="highway"/>
    <has-kv k="highway" modv="not" regv="footway|cycleway|path|service|track"/>
  </query>

  <!-- Get all linked ways without the current way --> 
  <difference into="linked_ways_only">
    <item set="linked_ways"/>
    <item set="this_way"/>
  </difference>
  <recurse from="linked_ways_only" type="way-node" into="linked_ways_only_nodes"/>

  <!-- Return all intersection nodes -->
  <query type="node">
    <item set="linked_ways_only_nodes"/>
    <item set="this_ways_nodes"/>
  </query>
  <print/>
</foreach>
```
##### Fetch nodes
```
/*
This query looks for nodes, ways and relations 
with the given key.
Choose your region and hit the Run button above!
*/
[timeout:100000];
// gather results
(
  // query part for: “"addr:housenumber"=*”
  node["addr:housenumber"]({{bbox}});
  way["addr:housenumber"]({{bbox}});
  relation["addr:housenumber"]({{bbox}});
);
// print results
out body;
>;
out skel qt;
```
##### Fetch ways
```
[timeout:25];
// gather results
(
  // query part for: “highway=*”
  way["highway"]({{bbox}});
);
// print results
out body;
>;
out skel qt;
```

## How to run
For running `road-distance.py` you need to set HERE Api key in environment variables.
To do that, create `.env` file and add the following line, where you replace `API_KEY`
with an actual api key:
```
HERE_API_KEY={API_KEY}
```

For running `cluster-utils.py` you need to install full metis library and python wrapper for metis.<br>
To install metis check: http://glaros.dtc.umn.edu/gkhome/metis/metis/download (if using Mac OS, you can just run `brew install metis`).<br>
For installing python wrapper for metis you can use: `pip install metis`. 
