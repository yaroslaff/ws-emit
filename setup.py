#!/usr/bin/env python3

import os
from setuptools import setup

def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()


setup(
    name='redis2websocket',
    version='0.0.1',
    scripts=['redis2websocket.py'],

    # install_requires=[],

    url='https://github.com/yaroslaff/redis2websocket',
    license='MIT',
    author='Yaroslav Polyakov',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    author_email='yaroslaff@gmail.com',
    description='Simple HTTP client which takes request data from redis',
    install_requires=[
        'redis',
        'requests',
        'inotify',
        'flask-socketio',
        'eventlet'
    ],
    data_files=[
        ('redis2websocket/contrib', [
            'contrib/redis2websocket.service',
            'contrib/redis2websocket'
            ]),
        ('redis2websocket/example', [
            'example/requirements.txt',
            'example/time.py',
            'example/dir2web.py',
            'example/subspy.py'
        ]),
        ('redis2websocket/example/templates', [
            'example/templates/time.html',
            'example/templates/dir2web.html'
        ])
    ],

    python_requires='>=3',
    classifiers=[
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',        
        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        # 'Programming Language :: Python :: 3.4',
    ]
)
