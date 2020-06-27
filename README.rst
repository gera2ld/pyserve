gera2ld.pyserve
===============

.. image:: https://img.shields.io/pypi/v/gera2ld-pyserve.svg

Serve asyncio and aiohttp servers, and show information for development.

Installation
------------

.. code-block:: sh

    $ pip install gera2ld-pyserve

    # or with extra `aio` if aiohttp applications are to be served
    $ pip install gera2ld-pyserve[aio]

Usage
-----

Run an asynchronous function in an infinite event loop:

.. code-block:: python

    from gera2ld.pyserve import run_forever

    async def main():
        # do stuff

    run_forever(main())

Start a server:

.. code-block:: python

    from gera2ld.pyserve import run_forever, start_server_asyncio

    def handle(reader, writer):
        # add more code here...

    run_forever(start_server_asyncio(handle, ':4000'))

Start a server with `aiohttp`:

.. code-block:: python

    from gera2ld.pyserve import run_forever, start_server_aiohttp
    from aiohttp import web

    app = web.Application()
    # add more code here...

    run_forever(start_server_aiohttp(app, ':4000'))
