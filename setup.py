#!/usr/bin/env python
from setuptools import find_packages, setup

# read the contents of README file
from os import path
from io import open  # for Python 2 and 3 compatibility

# get __version__ from _version.py
ver_file = path.join('termll', 'version.py')
with open(ver_file) as f:
    exec(f.read())

this_directory = path.abspath(path.dirname(__file__))


# read the contents of README.md
def readme():
    with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
        return f.read()


# read the contents of requirements.txt
with open(path.join(this_directory, 'requirements.txt'), encoding='utf-8') as f:
    requirements = f.read().splitlines()

setup(
    name='termll',
    version=__version__,
    description='Boost your terminal\'s intelligence with LLM: intuitive command assistance,'
                ' seamless customization, and predictive next steps at your fingertips.',
    long_description=readme(),
    long_description_content_type='text/markdown',
    author='Yizheng Huang',
    author_email='huangyz0918@gmail.com',
    url='https://github.com/huangyz0918/termll',
    download_url='https://github.com/huangyz0918/termll/archive/refs/heads/main.zip',
    keywords=['LLM', 'deep learning', 'MLOps', 'shell', 'neural networks', 'command line', 'terminal', 'autocomplete'],
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "termll=termll.cli:cli",
            "t=termll.cli:cli",
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    setup_requires=['setuptools>=38.6.0'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Education',
        'Intended Audience :: Financial and Insurance Industry',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        "Operating System :: OS Independent",
    ],
)
