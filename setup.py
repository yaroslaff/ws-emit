#!/usr/bin/env python3

import os
from setuptools import setup

def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()


setup(
    name='ws-emit',
    version='0.0.2',
    scripts=['ws-emit.py'],

    # install_requires=[],

    url='https://github.com/yaroslaff/ws-emit',
    license='MIT',
    author='Yaroslav Polyakov',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    author_email='yaroslaff@gmail.com',
    description='Easily emit websocket events from any sources using redis or HTTP interface',
    install_requires=[
        'redis',
        'requests',
        'inotify',
        'flask-socketio',
        'eventlet'
    ],
    data_files=[
        ('ws-emit/contrib', [
            'contrib/ws-emit.service',
            'contrib/ws-emit'
            ]),
        ('ws-emit/example', [
            'example/requirements.txt',
            'example/time.py',
            'example/dir2web.py',
            'example/subspy.py'
        ]),
        ('ws-emit/example/templates', [
            'example/templates/time.html',
            'example/templates/dir2web.html'
        ])
    ],

    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',        
        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        # 'Programming Language :: Python :: 3.4',
    ]
)
