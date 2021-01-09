# Opensky to CoT data converter

This simple python script fetches aircraft position data from [Opensky Network](https://opensky-network.org/)
and pushes it to Cursor-on-Target server (like [FreeTakServer](https://github.com/FreeTAKTeam/FreeTakServer), or
[Goatak](https://github.com/kdudkov/goatak)). Must work with ATAK server too.

## Usage

`python3 osky.py -h` to see all options

`python3 osky.py --proto broadcast` to send events via broadcast network, your CivTAK phone must be in one network with
your computer

### Usage with [FreeTakServer](https://github.com/FreeTAKTeam/FreeTakServer)

1. Run FreeTakServer:
`sudo docker run -p 8080:8080/tcp -p 8087:8087/tcp -e FTS_CONNECTION_MESSAGE="hello" -v fts_data:/data --name fts --restart unless-stopped freetakteam/freetakserver:1.2.5`
2. Run my script:
`python3 osky.py --proto tcp --port 8087 --addr 127.0.0.1`

