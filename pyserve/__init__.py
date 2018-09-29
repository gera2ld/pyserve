import os
import socket
import asyncio

def get_hosts(server):
    hosts = []
    for sock in server.sockets:
        hostname = sock.getsockname()
        host, port = hostname[:2]
        def add_port(host):
            if host is None: return
            return f'http://{host}:{port}'
        if host == '0.0.0.0':
            hosts.append(tuple(map(add_port, (
                'localhost',
                socket.gethostbyname(socket.gethostname()),
            ))))
        elif host == '::':
            hosts.append(tuple(map(add_port, ('[::1]', None))))
        else:
            hosts.append(tuple(map(add_port, (None, host))))
    return hosts

def wake_up(loop = None):
    if os.name == 'nt':
        if loop is None: loop = asyncio.get_event_loop()
        def wake_up_later():
            loop.call_later(.1, wake_up_later)
        wake_up_later()

def serve_forever(servers, loop = None):
    if loop is None: loop = asyncio.get_event_loop()
    print('=== Access URLs: ===')
    first = True
    if isinstance(servers, asyncio.base_events.Server):
        servers = [servers]
    for server in servers:
        hosts = get_hosts(server)
        for local, remote in hosts:
            if first:
                first = False
            else:
                print('---')
            if local is not None:
                print('Local:', local, sep='\t')
            if remote is not None:
                print('Remote:', remote, sep='\t')
    print('====================')
    wake_up(loop)
    loop.run_forever()
