=======================
Notes about development
=======================

Config file
===========

The minmal requirements are : paster compatible scheme (ConfigParser loadable
+ dedicated section name).

The practical requirement is being able to run the workers (decider, activity)
by simply specifying the config file (``caravan-decider -c myconfig.ini``).

Currently the config file system is far from ideal, it implicitely appends
arguments to the command line if the config key match an argparse argument.

