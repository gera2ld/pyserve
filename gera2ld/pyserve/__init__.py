import os
import socket
import asyncio

def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        # no real request is send
    finally:
        s.close()
    return ip

def get_hosts(server, scheme):
    for sock in server.sockets:
        hostname = sock.getsockname()
        if isinstance(hostname, str):
            # unix server
            yield hostname, None
        else:
            host, port = hostname[:2]
            def add_port(host):
                if host is None: return
                return f'{scheme}//{host}:{port}'
            if host == '0.0.0.0':
                yield add_port('localhost'), add_port(get_host_ip())
            elif host == '::':
                yield add_port('[::1]'), None
            else:
                yield None, add_port(host)

def wake_up(loop = None):
    if os.name == 'nt':
        if loop is None: loop = asyncio.get_event_loop()
        def wake_up_later():
            loop.call_later(.1, wake_up_later)
        wake_up_later()

def serve_forever(servers, loop=None, scheme='http:'):
    if loop is None: loop = asyncio.get_event_loop()
    print('====================')
    first = True
    if isinstance(servers, asyncio.base_events.Server):
        servers = [servers]
    for server in servers:
        hosts = get_hosts(server, scheme)
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
