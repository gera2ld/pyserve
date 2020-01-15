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

.. code-block:: python

    from gera2ld.pyserve import serve_asyncio

    def handle(reader, writer):
        # add more code here...

    serve_asyncio(handle, ':4000')

.. code-block:: python

    from gera2ld.pyserve import serve_aiohttp
    from aiohttp import web

    app = web.Application()
    # add more code here...

    serve_aiohttp(app, ':4000')
