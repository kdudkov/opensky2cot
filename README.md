# Opensky to CoT data converter

This simple python script fetches aircraft position data from [Opensky Network](https://opensky-network.org/)
and pushes it to Cursor-on-Target server (like [FreeTakServer](https://github.com/FreeTAKTeam/FreeTakServer), or
[Goatak](https://github.com/kdudkov/goatak)). Must work with ATAK server too.

## Usage

`python3 osky.py -h` to see all options

`python3 osky.py --proto broadcast` to send events via broadcast network, your CivTAK phone must be in one network with
your computer

`python3 osky.py --proto tcp --addr <fts_server_ip> --port <server_port>` to send events to FreeTakServer

