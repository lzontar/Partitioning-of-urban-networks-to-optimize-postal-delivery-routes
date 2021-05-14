# Partitioning of urban networks to optimize postal delivery routes

## Network structure
Here, we present the structure of our network, which will represent the city road infrastructure.

**Nodes** will represent crossroads. Each node will contain information about:
* its GPS coordinates: longitude and latitude,
* a list of nearby houses to which this crossroad is the closest crossroad.

**Edges** represent connections or combination of roads between two crossroads. 
Each edge is weighted by distance (in km) and time needed to get from one crossroad to another.
 
 
 Crossroads