#  Changelog

# Version 1.8
## Features
* Integration of the inverse kinematics for creature thanks to [ikpy](https://github.com/Phylliade/ikpy). An URDF file is required to calculate the ik and fk
* Any service like use_http (HttpRobotServer) or use_snap (SnapRobotServer) is started automatically in a daemon thread.
* poppy-simu can be used as a simulator.
* hardcode the list of robots to make to make the `from poppy.creatures import ...` faster (it was too slow in the Raspberry Pi).

## Bug fixes
* fix find_local_ip when there is no network
* poppy-service start Snap! in a chrome based browser if aivailable instead of the default one
* fix camelcase_to_underscore issue

# Version 1.6
## Features
* poppy-service : allow unspecified creature to be started if only one is installed
* add poppy-service and make poppy-snap depreciated. poppy-service can also start http and remote servers

## Bug fixes
* fix path issue of the utility to find any creatures

# Version 1.5
## Features
* add snap launcher
* Add utility to get all installed poppy creatures using pip.

## Bug fixes
* bind snap server to all interface by default (0.0.0.0)


# Version 1.3
## Features
* Add PoppyErgoJr in the creatures
* Add the possibility to start a snap server directly in the creature
* change 'simulated' to 'simulator' in the API
