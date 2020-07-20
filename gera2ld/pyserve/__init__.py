import os
import socket
import asyncio
from .host import Host

web = None

def load_aiohttp(throw=True):
    global web
    global load_aiohttp
    try:
        from aiohttp import web
    except:
        pass
    def postload_aiohttp(throw=True):
        if throw:
            assert web is not None, 'module is not found: aiohttp'
    load_aiohttp = postload_aiohttp
    return load_aiohttp(throw)

class UrlItem:
    TYPE_LOCAL = 'local', 'Local:'
    TYPE_REMOTE = 'remote', 'Remote:'

    def __init__(self, type, data):
        self.type = type
        self.data = data

    def to_str(self):
        return f'{self.type[1]}\t{self.data}'

def get_host_ip(target=('8.8.8.8', 53)):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(target)
        ip = s.getsockname()[0]
        # no real request is send
    finally:
        s.close()
    return ip

def is_path(path):
    if not isinstance(path, str): return False
    return path.startswith('/') or path.startswith('file://')

async def start_server(handle, hostinfo):
    if is_path(hostinfo):
        try:
            os.remove(hostinfo)
        except FileNotFoundError:
            pass
        server = await asyncio.start_unix_server(handle, path=hostinfo)
        os.chmod(hostinfo, 0o666)
        return server
    host = Host(hostinfo)
    return await asyncio.start_server(handle, host=host.hostname, port=host.port)

async def start_aio_server(handle, hostinfo):
    load_aiohttp()
    if isinstance(handle, web.Application):
        runner = web.AppRunner(handle)
    else:
        runner = web.ServerRunner(web.Server(handle))
    await runner.setup()
    if is_path(hostinfo):
        try:
            os.remove(hostinfo)
        except FileNotFoundError:
            pass
        site = web.UnixSite(runner, hostinfo)
        await site.start()
        os.chmod(hostinfo, 0o666)
    else:
        host = Host(hostinfo)
        site = web.TCPSite(runner, host=host.hostname, port=host.port)
        await site.start()
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

def get_server_hosts(servers, scheme):
    for server in servers:
        if isinstance(server, asyncio.base_events.Server):
            yield get_url_items([sock.getsockname() for sock in server.sockets], scheme)
        else:
            load_aiohttp(throw=False)
            if web is not None and isinstance(server, web.BaseRunner):
                yield get_url_items(server.addresses)

def wake_up():
    if os.name == 'nt':
        loop = asyncio.get_event_loop()
        def wake_up_later():
            loop.call_later(.1, wake_up_later)
        wake_up_later()

def run_forever(aw=None):
    wake_up()
    loop = asyncio.get_event_loop()
    if aw is not None:
        loop.run_until_complete(aw)
    loop.run_forever()

def repr_urls(hosts):
    yield '===================='
    first_host = True
    for groups in hosts:
        if first_host:
            first_host = False
        else:
            yield '***'
        first_group = True
        for group in groups:
            if first_group:
                first_group = False
            else:
                yield '---'
            for item in group:
                yield item.to_str()
    yield '===================='

def print_urls(hosts):
    for line in repr_urls(hosts):
        print(line)

async def start_server_asyncio(handle, hostinfo, scheme='http:'):
    server = await start_server(handle, hostinfo)
    print_urls(get_server_hosts([server], scheme))
    return server

async def start_server_aiohttp(handle, hostinfo, scheme='http:'):
    server = await start_aio_server(handle, hostinfo)
    print_urls(get_server_hosts([server], scheme))
    return server
