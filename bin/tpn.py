#!/usr/bin/env python

import os
import sys

def join_path(*args):
    return os.path.abspath(os.path.normpath(os.path.join(*args)))

try:
    from tpn.cli import main
except ImportError:
    path = os.path.abspath(__file__)
    if os.path.islink(path):
        target = os.readlink(path)
        if target.endswith('tpn/bin/tpn'):
            libdir = target[:-len('bin/tpn')-1]
            sys.path.insert(0, libdir)
    else:
        libdir = join_path(path, '../../lib')
        sys.path.insert(0, libdir)

    from tpn.cli import main

if __name__ == '__main__':
    main()

# vi:set ts=8 sw=4 sts=4 expandtab tw=78 syntax=python:
