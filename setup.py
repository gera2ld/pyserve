from setuptools import setup
from codecs import open
from os import path

__version__ = '0.0.4'

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

# get the dependencies and installs
# with open(path.join(here, 'requirements.txt'), encoding='utf-8') as f:
#     all_reqs = f.read().split('\n')
all_reqs = []

install_requires = [x.strip() for x in all_reqs if 'git+' not in x]
dependency_links = [x.strip().replace('git+', '') for x in all_reqs if x.startswith('git+')]

setup(
    name='gera2ld-pyserve',
    version=__version__,
    description='Start serving an asyncio.Server',
    long_description=long_description,
    url='https://github.com/gera2ld/pyserve',
    download_url='https://github.com/gera2ld/pyserve/tarball/' + __version__,
    license='BSD',
    classifiers=[
      'Development Status :: 3 - Alpha',
      'Intended Audience :: Developers',
      'Programming Language :: Python :: 3',
    ],
    keywords='',
    packages=['gera2ld.pyserve'],
    include_package_data=True,
    author='Gerald',
    install_requires=install_requires,
    dependency_links=dependency_links,
    author_email='i@gerald.top'
)
