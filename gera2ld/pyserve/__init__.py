import os
import socket
import asyncio

class UrlItem:
    TYPE_LOCAL = 'local', 'Local:'
    TYPE_REMOTE = 'remote', 'Remote:'

    def __init__(self, type, data):
        self.type = type
        self.data = data

    def to_str(self):
        return f'{self.type[1]}\t{self.data}'

def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        # no real request is send
    finally:
        s.close()
    return ip

def get_url_pairs(hosts, scheme):
    for host in hosts:
        if isinstance(host, str):
            # unix server
            yield host, None
        else:
            hostname, port = host[:2]
            def add_port(hostname):
                if hostname is None: return
                return f'{scheme}//{hostname}:{port}'
            if hostname == '0.0.0.0':
                yield add_port('localhost'), add_port(get_host_ip())
            elif hostname == '::':
                yield add_port('[::1]'), None
            else:
                yield None, add_port(hostname)

def get_url_items(hosts, scheme='http:'):
    for local, remote in get_url_pairs(hosts, scheme):
        items = []
        if local is not None:
            items.append(UrlItem(type=UrlItem.TYPE_LOCAL, data=local))
        if remote is not None:
            items.append(UrlItem(type=UrlItem.TYPE_REMOTE, data=remote))
        yield items

def get_asyncio_server_hosts(server, scheme):
    assert isinstance(server, asyncio.base_events.Server)
    yield from get_url_items([sock.getsockname() for sock in server.sockets], scheme)

def wake_up(loop=None):
    if os.name == 'nt':
        if loop is None: loop = asyncio.get_event_loop()
        def wake_up_later():
            loop.call_later(.1, wake_up_later)
        wake_up_later()

def run_forever(loop=None):
    if loop is None: loop = asyncio.get_event_loop()
    wake_up(loop)
    loop.run_forever()

def print_urls(hosts):
    print('====================')
    first_host = True
    for groups in hosts:
        if first_host:
            first_host = False
        else:
            print('***')
        first_group = True
        for group in groups:
            if first_group:
                first_group = False
            else:
                print('---')
            for item in group:
                print(item.to_str())
    print('====================')

def serve_forever(servers, loop=None, scheme='http:'):
    if not isinstance(servers, (list, tuple)):
        servers = [servers]
    print_urls(get_asyncio_server_hosts(server, scheme) for server in servers)
    run_forever(loop)
