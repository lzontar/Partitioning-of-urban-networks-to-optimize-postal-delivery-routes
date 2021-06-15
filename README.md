# Partitioning of urban networks to optimize postal delivery routes

## Network structure
Here, we present the structure of our network, which will represent the city road infrastructure.

**Nodes** will represent crossroads. Each node will contain information about:
* its GPS coordinates: longitude and latitude,
* a list of nearby houses to which this crossroad is the closest crossroad.

**Edges** represent connections or combination of roads between two crossroads. 
Each edge is weighted by distance (in km) and time needed to get from one crossroad to another.
 
 
Crossroads

## How to run
For running `road-distance.py` you need to set HERE Api key in environment variables.
To do that, create `.env` file and add the following line, where you replace `API_KEY`
with an actual api key:
```
HERE_API_KEY={API_KEY}
```