# FlexRadio Discovery Pakcet Proxy

This project was created to allow connecting to a FlexRadio over a VPN as an
alternative to using SmartLink.

## Why?

FlexRadio does not want to provide a way to connect to the radio by IP address.
The only way to connect to the radio is by recieving a discovery packet from the radio.
This is a problem if you want to connect to the radio from a different network when broadcast packets are not forwarded.

## How?

The proxy consists of two Python 3 scripts.

`flex_proxy.py` is the main script that listens for discovery packets and forwards them to the client.
It listens for UDP discovery packets on port 4992 and forwards the payload to all clients connected to the TCP socket on port 4996.

`client.py` connects to the proxy via the TCP socket on port 4996. When a message is recieved, it re-broadcasts it as a UDP packet on port 4992.

## Usage

None of the two scripts require any external libraries.
All libraries used are part of the Python 3 standard library:

- `argparse`
- `re`
- `select`
- `socket`
- `sys`
- `time`

### Server

```
python3 flex_proxy.py
```

The TCP socket port can be changed by changing the `PORT` variable in `flex_proxy.py`.

### Client

```
python3 client.py [ip address]
```

The default IP address is `localhost`.
It can be changed by changing the `HOST` variable in `client.py` or by passing the IP address as an argument.
