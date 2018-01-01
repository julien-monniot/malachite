## Malachite
##### Simple L3 network graphing tool based on napalm and plotly.

This is the core package for malachite. 
It offers a standard python package that should be able to :
- connect to network appliances and extract arp tables and list of local IPs
- format these data and create/enrich a data model
- use this data model as the base for drawing a 3D graph with python-igraph and ploty.

Currently the use of this package is extremely limited and tested only for Arista vEOS platform
(although other devices should be supported too, as the required Napalm features
for this project are very basic).
