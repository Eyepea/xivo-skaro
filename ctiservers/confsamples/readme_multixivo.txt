- my current usage of multi-xivo conf is to have, on 3 separate consoles :

./xivo_daemon -d -i 192.168.0.182 -p /tmp/xivo_daemon.pid1 -P    0 -C file:///myhome/cs_cfg_over_puteaux.json
./xivo_daemon -d -i 192.168.0.182 -p /tmp/xivo_daemon.pid2 -P 1000 -C file:///myhome/cs_cfg_over_limonest.json
./xivo_daemon -d -i 192.168.0.182 -p /tmp/xivo_daemon.pid3 -P 2000 -C file:///myhome/cs_cfg_over_quebec.json

- the config structure in these json files is one of the kind I'd like to get from the WEBI config
- maybe the IP above, as well as inside those .json extra files, is to be changed

