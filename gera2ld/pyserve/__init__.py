import os
import socket
import asyncio
import urllib

try:
    from aiohttp import web
except:
    web = None

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

def parse_addr(host, default=('', 0)):
    if isinstance(host, tuple):
        hostname, port = host
        return { 'host': hostname, 'port': port }
    if not ':' in host:
        # assume path to unix socket
        return { 'path': host }
    result = urllib.parse.urlparse('//' + host)
    hostname = result.hostname
    if hostname is None: hostname = default[0]
    port = result.port
    if port is None: port = default[0]
    return { 'host': hostname, 'port': port }

async def start_server(handle, hostinfo):
    if isinstance(hostinfo, str):
        hostinfo = parse_addr(hostinfo)
    path = hostinfo.get('path')
    if path:
        try:
            os.remove(path)
        except FileNotFoundError:
            pass
        server = await asyncio.start_unix_server(handle, path=path)
        os.chmod(path, 0o666)
        return server
    return await asyncio.start_server(handle, host=hostinfo['host'], port=hostinfo['port'])

async def start_aio_server(handle, hostinfo):
    assert web is not None, 'module is not found: aiohttp'
    if isinstance(handle, web.Application):
        runner = web.AppRunner(handle)
    else:
        runner = web.ServerRunner(web.Server(handle))
    await runner.setup()
    if isinstance(hostinfo, str):
        hostinfo = parse_addr(hostinfo)
    path = hostinfo.get('path')
    if path:
        try:
            os.remove(path)
        except FileNotFoundError:
            pass
        site = web.UnixSite(runner, path)
    else:
        site = web.TCPSite(runner, host=hostinfo['host'], port=hostinfo['port'])
    await site.start()
    if path:
        os.chmod(path, 0o666)
    return runner

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

def get_server_hosts(servers, scheme='http:'):
    for server in servers:
        if isinstance(server, asyncio.base_events.Server):
            yield get_url_items([sock.getsockname() for sock in server.sockets], scheme)
        elif web is not None and isinstance(server, web.BaseRunner):
            yield get_url_items(server.addresses)

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
    print_urls(get_server_hosts(servers, scheme))
    run_forever(loop)

def serve_asyncio(handle, hostinfo, **kw):
    loop = asyncio.get_event_loop()
    server = loop.run_until_complete(start_server(handle, hostinfo))
    serve_forever([server], loop, **kw)

def serve_aiohttp(handle, hostinfo, **kw):
    loop = asyncio.get_event_loop()
    server = loop.run_until_complete(start_aio_server(handle, hostinfo))
    serve_forever([server], loop, **kw)
