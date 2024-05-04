#===============================================================================
# Imports
#===============================================================================
import os
import re
import sys
import copy
import json
import time
import shutil
import inspect
import hashlib
import calendar
import datetime
import itertools
import subprocess
import collections

try:
    import cStringIO as StringIO
except ImportError:
    import io
    StringIO = io.StringIO

from bisect import (
    bisect_left,
    bisect_right,
)

from datetime import (
    timezone,
    timedelta,
)

from os.path import (
    join,
    isdir,
    abspath,
    dirname,
    basename,
    splitext,
    normpath,
)

from itertools import (
    chain,
    repeat,
)

from collections import (
    namedtuple,
    defaultdict,
)

from pprint import (
    pformat,
)

from functools import (
    wraps,
    partial,
)

from subprocess import (
    Popen,
    PIPE,
)

from csv import reader as csv_reader

from tpn import (
    logic,
)


#===============================================================================
# Globals
#===============================================================================
SHORT_MONTHS = (
    'Jan',
    'Feb',
    'Mar',
    'Apr',
    'May',
    'June',
    'July',
    'Aug',
    'Sept',
    'Oct',
    'Nov',
    'Dec',
)
SHORT_MONTHS_UPPER = [ m.upper() for m in SHORT_MONTHS ]

SHORT_MONTHS_SET = set(SHORT_MONTHS)
SHORT_MONTHS_UPPER_SET = set(SHORT_MONTHS_UPPER)

EPOCH_AS_FILETIME = 116444736000000000  # January 1, 1970 as filetime
HUNDREDS_OF_NS = 10000000

is_linux = (sys.platform.startswith('linux'))
is_darwin = (sys.platform == 'darwin')
is_win32 = (sys.platform == 'win32')
is_cygwin = (sys.platform == 'cygwin')

#===============================================================================
# Helper Methods
#===============================================================================
def bytes_to_eb(b):
    return '%0.1f PB' % (float(b)/1024.0/1024.0/1024.0/1024.0/1024.0/1024.0)

def bytes_to_pb(b):
    return '%0.1f PB' % (float(b)/1024.0/1024.0/1024.0/1024.0/1024.0)

def bytes_to_tb(b):
    return '%0.1f TB' % (float(b)/1024.0/1024.0/1024.0/1024.0)

def bytes_to_gb(b):
    return '%0.1f GB' % (float(b)/1024.0/1024.0/1024.0)

def bytes_to_mb(b):
    return '%0.1f MB' % (float(b)/1024.0/1024.0)

def bytes_to_kb(b):
    return '%0.1f KB' % (float(b)/1024.0)

def bytes_to_b(b):
    return '%d B' % b

bytes_conv_table = [
    bytes_to_b,
    bytes_to_kb,
    bytes_to_mb,
    bytes_to_gb,
    bytes_to_tb,
    bytes_to_pb,
    bytes_to_eb,
]

def bytes_to_human(b):
    n = int(b)
    i = 0
    while n >> 10:
        n >>= 10
        i += 1
    return bytes_conv_table[i](b)

def milliseconds_to_microseconds(ms):
    return ms * 1000

def milliseconds_to_ticks(ms, frequency):
    nanos_per_tick = 1.0 / float(frequency)
    nanos = ms * 1e-9
    ticks = nanos / nanos_per_tick
    return ticks

def datetime_to_filetime(dt):
    if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
        dt = dt.replace(tzinfo=timezone.utc)
    filetime = EPOCH_AS_FILETIME + (calendar.timegm(dt.timetuple()) * HUNDREDS_OF_NS)
    filetime += (dt.microsecond * 10)
    return filetime

def filetime_utc_to_datetime_utc(ft):
    micro = ft / 10
    (seconds, micro) = divmod(micro, 1000000)
    (days, seconds) = divmod(seconds, 86400)
    base = datetime.datetime(1601, 1, 1, tzinfo=datetime.timezone.utc)
    delta = timedelta(days, seconds, micro)
    dt = base + delta
    return dt

def datetime_utc_to_local_tz(dt):
    return dt.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None)

def filetime_utc_to_local_tz(ft):
    return datetime_utc_to_local_tz(filetime_utc_to_datetime_utc(ft))

def datetime_to_str(dt, fmt=None):
    if fmt is None:
        fmt = '%Y-%m-%d %H:%M:%S'
    return dt.strftime(fmt)

def nanos_per_frame(fps):
    return (1.0 / float(fps)) * 1e9

def frames_per_second_to_ticks(fps, frequency=None):
    return ((1.0 / float(fps)) / (1.0 / float(frequency)))

def round_to_pages(size, page_size=4096):
    return (
        (size + page_size - 1) & ~(page_size -1)
    )

def hex_zfill(h, bits=64):
    s = str(hex(h | (1 << bits+4)))[3:]
    div = (bits >> 3)
    high = s[:div]
    low = s[div:]
    return '0x%s`%s' % (high, low)

def bin_zfill(h, bits=64):
    s = str(bin(h | (1 << bits+1)))[3:]
    div = (bits >> 1)
    high = s[:div]
    low = s[div:]
    return '0b%s`%s' % (high, low)

def percent_change(old, new):
    diff = float(old) - float(new)
    return (diff / old) * 100.0

def fold_increase(old, new):
    diff = float(new) - float(old)
    fold = diff / new
    return fold

def fold_decrease(old, new):
    diff = float(old) - float(new)
    fold = diff / old
    return fold

def align_down(address, alignment):
    """
    >>> hex(align_down(0x00007ffd11483294, 2)).replace('L', '')
    '0x7ffd11483294'

    >>> hex(align_down(0x00007ffd11483294, 4)).replace('L', '')
    '0x7ffd11483294'

    >>> hex(align_down(0x00007ffd11483294, 8)).replace('L', '')
    '0x7ffd11483290'

    >>> hex(align_down(0x00007ffd11483294, 16)).replace('L', '')
    '0x7ffd11483290'

    >>> hex(align_down(0x00007ffd11483294, 256)).replace('L', '')
    '0x7ffd11483200'

    >>> hex(align_down(0x00007ffd11483294, 512)).replace('L', '')
    '0x7ffd11483200'

    """
    return address & ~(alignment-1)

def test_align_down():
    return [
        hex(align_down(0x00007ffd11483294, 2)).replace('L', ''),
        hex(align_down(0x00007ffd11483294, 4)).replace('L', ''),
        hex(align_down(0x00007ffd11483294, 8)).replace('L', ''),
        hex(align_down(0x00007ffd11483294, 16)).replace('L', ''),
        hex(align_down(0x00007ffd11483294, 256)).replace('L', ''),
        hex(align_down(0x00007ffd11483294, 512)).replace('L', ''),
    ]

def align_up(address, alignment):
    """
    >>> hex(align_up(0x00007ffd11483294, 2)).replace('L', '')
    '0x7ffd11483294'

    >>> hex(align_up(0x00007ffd11483294, 4)).replace('L', '')
    '0x7ffd11483294'

    >>> hex(align_up(0x00007ffd11483294, 8)).replace('L', '')
    '0x7ffd11483298'

    >>> hex(align_up(0x00007ffd11483294, 16)).replace('L', '')
    '0x7ffd114832a0'

    >>> hex(align_up(0x00007ffd11483294, 256)).replace('L', '')
    '0x7ffd11483300'

    >>> hex(align_up(0x00007ffd11483294, 512)).replace('L', '')
    '0x7ffd11483400'
    """
    return (address + (alignment-1)) & ~(alignment-1)

def test_align_up():
    return [
        hex(align_up(0x00007ffd11483294, 2)).replace('L', ''),
        hex(align_up(0x00007ffd11483294, 4)).replace('L', ''),
        hex(align_up(0x00007ffd11483294, 8)).replace('L', ''),
        hex(align_up(0x00007ffd11483294, 16)).replace('L', ''),
        hex(align_up(0x00007ffd11483294, 256)).replace('L', ''),
        hex(align_up(0x00007ffd11483294, 512)).replace('L', ''),
    ]

def trailing_zeros(address):
    count = 0
    addr = bin(address)
    for c in reversed(addr):
        if c != '0':
            break
        count += 1
    return count

def popcount_slow(n):
    return bin(n).count('1')

def popcount(n):
    n = (n & 0x5555555555555555) + ((n & 0xAAAAAAAAAAAAAAAA) >> 1)
    n = (n & 0x3333333333333333) + ((n & 0xCCCCCCCCCCCCCCCC) >> 2)
    n = (n & 0x0F0F0F0F0F0F0F0F) + ((n & 0xF0F0F0F0F0F0F0F0) >> 4)
    n = (n & 0x00FF00FF00FF00FF) + ((n & 0xFF00FF00FF00FF00) >> 8)
    n = (n & 0x0000FFFF0000FFFF) + ((n & 0xFFFF0000FFFF0000) >> 16)
    n = (n & 0x00000000FFFFFFFF) + ((n & 0xFFFFFFFF00000000) >> 32)
    return n

def get_address_alignment(address):
    """
    >>> get_address_alignment(0x00007ffd11483294)
    4
    >>> get_address_alignment(0x00007ffd114832c1)
    1
    >>> get_address_alignment(0x00007ffd11483298)
    8
    >>> get_address_alignment(0x00007ffd11483200)
    512
    """
    return 1 << trailing_zeros(address)

def is_power_of_2(x):
    return (x & (x - 1)) == 0

def round_up_power_of_2(x):
    return 1<<(x-1).bit_length()

def round_up_next_power_of_2(x):
    if is_power_of_2(x):
        x += 1
    return round_up_power_of_2(x)

def lower(l):
    return [ s.lower() for s in l ]

def iterable(i):
    if not i:
        return []
    return (i,) if not hasattr(i, '__iter__') else i

def isiterable(i):
    return hasattr(i, '__iter__') or hasattr(i, 'next')

def try_int(i):
    if not i:
        return
    try:
        i = int(i)
    except ValueError:
        return
    else:
        return i

def is_int(i):
    try:
        int(i)
    except ValueError:
        return False
    else:
        return True

def progressbar(i, total=None, leave=False):
    try:
        from tqdm import tqdm
        return tqdm(i, total=total, leave=leave)
    except ImportError:
        import sys
        e = sys.stderr.write
        e("tqdm not installed, not displaying progressbar\n")
        e("tip: run `pip install tqdm` from commandline to fix\n")
        return i

def null_progressbar(r, *args, **kwds):
    return iter(r)

def flatten(l):
    return [ item for sublist in l for item in sublist ]

def version_combinations(s):
    """
    >>> version_combinations('5.10.0')
    ['5.10.0', '5.10', '5']
    >>> version_combinations('3.2')
    ['3.2', '3']
    >>> version_combinations('6')
    ['6']
    """
    if '.' not in s:
        return [s] if try_int(s) else None

    ints = s.split('.')
    if not all(i.isdigit() for i in ints):
        return None

    return [ '.'.join(ints[:x]) for x in reversed(range(1, len(ints)+1)) ]

def invert_defaultdict_by_value_len(d):
    i = defaultdict(list)
    for (k, v) in d.items():
        i[len(v)].append(k)
    return i

def ensure_sorted(d):
    keys = d.keys()
    sorted_keys = [ k for k in sorted(keys) ]
    assert keys == sorted_keys, (keys, sorted_keys)

def yield_scalars(obj, scalar_types=None):
    if not scalar_types:
        try:
            scalar_types = frozenset((int, float, str, unicode))
        except NameError:
            scalar_types = frozenset((int, float, str))

    for k in dir(obj.__class__):
        v = getattr(obj, k)
        t = type(v)
        y = None
        if t in scalar_types:
            y = (k, v)
        if y:
            yield y

def generate_repr(obj, exclude=None, include=None, yielder=None):
    cls = obj.__class__
    ex = set(exclude if exclude else [])
    inc = set(include if include else [])
    yielder = yielder or yield_scalars
    p = lambda v: v if (not v or isinstance(v, int)) else '"%s"' % v
    return '<%s %s>' % (
        (cls.__name__, ', '.join(
            '%s=%s' % (k, p(v)) for (k, v) in (
                (k, v) for (k, v) in yielder(obj) if (
                    k in inc or (
                        k[0] != '_' and
                        k not in ex and
                        not k.endswith('_id')
                    )
                )
            ) if (True if inc else bool(v))
        ))
    )

def hexdump(string, remove_bom=True, encoding='utf-16', cols=12,
            add_nul=True, return_rows=False, clipboard=False,
            indent=4):
    s = string.encode(encoding)
    if remove_bom:
        s = s[2:]

    if add_nul:
        if encoding == 'utf-16':
            s += b'\x00\x00'
        else:
            s += b'\x00'

    chars = [ f'{c:#04x}' for c in s ]
    rows = []
    start = 0 - cols
    size = len(chars)
    while True:
        start += cols
        assert start <= size, (start, size)
        if start == size:
            break
        end = start + cols
        if end > size:
            rows.append(chars[start:size])
            break

        rows.append(chars[start:end])

    if return_rows:
        return rows

    lines = []
    for row in rows:
        line = ', '.join(row)
        if indent:
            line = f"{' ' * indent}{line}"
        lines.append(line)

    text = ',\n'.join(lines)

    if clipboard:
        from tpn.clipboard import cb
        cb(text)

    return text

def get_query_slices(total_size, ideal_chunk_size=None, min_chunk_size=None):
    from .config import get_config
    conf = get_config()
    if not ideal_chunk_size:
        ideal_chunk_size = conf.sqlalchemy_ideal_chunk_size
    if not min_chunk_size:
        min_chunk_size = conf.sqlalchemy_min_chunk_size

    if ideal_chunk_size >= total_size:
        yield (0, total_size)
        raise StopIteration

    start = 0 - ideal_chunk_size
    while True:
        start += ideal_chunk_size
        end = start + ideal_chunk_size - 1
        if end > total_size:
            yield (start, total_size)
            raise StopIteration

        next_start = start + ideal_chunk_size
        next_end = min(next_start + ideal_chunk_size - 1, total_size)
        if next_end - next_start < min_chunk_size:
            yield (start, total_size)
            raise StopIteration

        yield (start, end)

def stream(query, size=None, limit=None,
                  ideal_chunk_size=None,
                  min_chunk_size=None):

    if limit:
        query.limit(limit)

    if not size:
        size = query.count()

    slice_offsets = get_query_slices(
        size if not limit else min(size, limit),
        ideal_chunk_size=ideal_chunk_size,
        min_chunk_size=min_chunk_size,
    )

    for (start, end) in slice_offsets:
        for result in query.slice(start, end):
            yield result

def stream_results(query):
    size = query.count()
    return progressbar(stream(query, size), total=size, leave=True)

def ensure_unique(d):
    seen = set()
    for k in d:
        assert k not in seen
        seen.add(k)

def endswith(string, suffixes):
    """
    Return True if string ``s`` endswith any of the items in sequence ``l``.
    """
    for suffix in iterable(suffixes):
        if string.endswith(suffix):
            return True
    return False

def startswith(string, prefixes):
    """
    Return True if string ``s`` startswith any of the items in sequence ``l``.
    """
    for prefix in iterable(prefixes):
        if string.startswith(prefix):
            return True
    return False

def extract_columns(line, cols, sep='|'):
    values = []
    last_ix = 0
    ix = 0
    i = 0
    for col_ix in cols:
        assert col_ix > i
        while True:
            i += 1
            ix = line.find(sep, last_ix)
            if i == col_ix:
                values.append(line[last_ix:ix])
                last_ix = ix + 1
                break
            else:
                last_ix = ix + 1
    return values

def extract_column(line, col, sep='|'):
    return extract_columns(line, (col,))[0]

def strip_crlf(line):
    if line[-2:] == u'\r\n':
        line = line[:-2]
    elif line[-1:] == u'\n':
        line = line[:-1]
    return line

def strip_empty_lines(text):
    while True:
        (text, count) = re.subn('\n *\n', '\n', text)
        if count == 0:
            break
    return text

def cr_to_crlf(text):
    text = text.replace('\n', '\r\n')
    # Just in case it's already \r\n:
    text = text.replace('\r\r', '\r')
    return text

def dedent(text, size=4):
    prefix = ' ' * size
    lines = text.splitlines()
    ix = len(lines[0])
    sep = '\r\n' if text[ix-1:ix+1] == '\r\n' else '\n'
    pattern = re.compile('^%s' % prefix)
    return sep.join(pattern.sub('', line) for line in lines)

def indent(text, size=4):
    prefix = ' ' * size
    lines = text.splitlines()
    ix = len(lines[0])
    sep = '\r\n' if text[ix-1:ix+1] == '\r\n' else '\n'
    pattern = re.compile('^')
    return sep.join(pattern.sub(prefix, line) for line in lines)

def char_count(text):
    """
    Returns a dict where keys represent each unique character occuring in text,
    and values represent the number of times that character occurred.
    """
    r = defaultdict(int)
    for c in text:
        r[c] += 1
    return r

def text_to_html(text):
    return ''.join('&#%d;' % ord(c) for c in text)

def clone_dict(d):
    """
    Helper method intended to be used with defaultdicts -- returns a new dict
    with all defaultdicts converted to dicts (recursively).
    """
    r = {}
    for (k, v) in d.iteritems():
        if hasattr(v, 'iteritems'):
            v = clone_dict(v)
        elif isinstance(v, set):
            v = [ i for i in v ]
        r[k] = v
    return r

def find_all_files_ending_with(dirname, suffix):
    results = []
    from .path import join_path
    for (root, dirs, files) in os.walk(dirname):
        results += [
            join_path(root, file)
                for file in files
                    if file.endswith(suffix)
        ]
    return results

def guess_gzip_filesize(path):
    """
    Only works when file is <= 2GB.
    """
    import struct
    with open(path, 'rb') as f:
        f.seek(-4, 2)
        size = struct.unpack('<i', f.read())[0]
    return size

def requires_context(f):
    @wraps(f)
    def wrapper(*args, **kwds):
        obj = args[0]
        fname = f.func_name
        n = '%s.%s' % (obj.__class__.__name__, fname)
        if not obj.entered:
            m = "%s must be called from within an 'with' statement." % n
            raise RuntimeError(m)
        elif obj.exited:
            allow = False
            try:
                allow = obj.allow_reentry_after_exit
            except AttributeError:
                pass
            if not allow:
                m = "%s can not be called after leaving a 'with' statement."
                raise RuntimeError(m % n)
            else:
                obj.exited = False
        return f(*args, **kwds)
    return wrapper

def implicit_context(f):
    @wraps(f)
    def wrapper(*args, **kwds):
        obj = args[0]
        fname = f.func_name
        n = '%s.%s' % (obj.__class__.__name__, fname)
        if not obj.entered:
            with obj as obj:
                return f(*args, **kwds)
        else:
            return f(*args, **kwds)
    return wrapper

if is_linux:
    def set_process_name(name):
        import ctypes
        libc = ctypes.cdll.LoadLibrary('libc.so.6')
        PR_SET_NAME = 15
        libc.prctl(PR_SET_NAME, name, 0, 0, 0)

    def get_openai_key(path=None):
        command = ['gpg', '-d', '--batch', '--quiet']
        if path is None:
            path = '~/.zsh/openai_key.asc'
        path = os.path.expanduser(path)
        if not os.path.exists(path):
            raise RuntimeError('File not found: %s' % path)
        command.append(path)
        return subprocess.check_output(command).strip().decode('utf-8')

class classproperty(property):
    def __get__(self, obj, type_):
        return self.fget.__get__(None, type_)()

    def __set__(self, obj, value):
        cls = type(obj)
        return self.fset.__get__(None, cls)(value)

def add_linesep_if_missing(s):
    return '' if not s else (s if s[-1] is os.linesep else s + os.linesep)

def strip_linesep_if_present(s):
    if not s:
        return ''
    if s.endswith('\r\n'):
        return s[-2]
    elif s[-1] == '\n':
        return s[:-1]
    else:
        return s

def prepend_warning_if_missing(s):
    return add_linesep_if_missing(
        s if s.startswith('warning: ') else 'warning: ' + s
    )

def prepend_error_if_missing(s):
    return add_linesep_if_missing(
        s if s.startswith('error: ') else 'error: ' + s
    )

def render_text_table(rows, **kwds):
    banner = kwds.get('banner')
    footer = kwds.get('footer')
    output = kwds.get('output', sys.stdout)
    balign = kwds.get('balign', str.center)
    formats = kwds.get('formats')
    special = kwds.get('special')
    rows = list(rows)
    if not formats:
        formats = lambda: chain((str.ljust,), repeat(str.rjust))

    cols = len(rows[0])
    paddings = [
        max([len(str(r[i])) for r in rows]) + 2
            for i in range(cols)
    ]

    length = sum(paddings) + cols
    strip = '+%s+' % ('-' * (length-1))
    out = list()
    if banner:
        lines = iterable(banner)
        banner = [ strip ] + \
                 [ '|%s|' % balign(l, length-1) for l in lines ] + \
                 [ strip, ]
        out.append('\n'.join(banner))

    rows.insert(1, [ '-', ] * cols)
    out += [
        '\n'.join([
            k + '|'.join([
                fmt(str(column), padding, (
                    special if column == special else fill
                )) for (column, fmt, padding) in zip(row, fmts(), paddings)
            ]) + k for (row, fmts, fill, k) in zip(
                rows,
                chain(
                    repeat(lambda: repeat(str.center,), 1),
                    repeat(formats,)
                ),
                chain((' ',), repeat('-', 1), repeat(' ')),
                chain(('|', '+'), repeat('|'))
            )
        ] + [strip,])
    ]

    if footer:
        footers = iterable(footer)
        footer = [ strip ] + \
                 [ '|%s|' % balign(f, length-1) for f in footers ] + \
                 [ strip, '' ]
        out.append('\n'.join(footer))

    output.write(add_linesep_if_missing('\n'.join(out)))

def render_unicode_table(rows, **kwds):
    """
    Unicode version of above.  Such code repetition!
    """
    banner = kwds.get('banner')
    footer = kwds.get('footer')
    output = kwds.get('output', sys.stdout)
    balign = kwds.get('balign', unicode.center)
    formats = kwds.get('formats')
    special = kwds.get('special')
    rows = list(rows)
    if not formats:
        formats = lambda: chain((unicode.ljust,), repeat(unicode.rjust))

    cols = len(rows[0])
    paddings = [
        max([len(unicode(r[i])) for r in rows]) + 2
            for i in range(cols)
    ]

    length = sum(paddings) + cols
    strip = u'+%s+' % (u'-' * (length-1))
    out = list()
    if banner:
        lines = iterable(banner)
        banner = [ strip ] + \
                 [ u'|%s|' % balign(l, length-1) for l in lines ] + \
                 [ strip, ]
        out.append(u'\n'.join(banner))

    rows.insert(1, [ u'-', ] * cols)
    out += [
        u'\n'.join([
            k + u'|'.join([
                fmt(unicode(column), padding, (
                    special if column == special else fill
                )) for (column, fmt, padding) in zip(row, fmts(), paddings)
            ]) + k for (row, fmts, fill, k) in zip(
                rows,
                chain(
                    repeat(lambda: repeat(unicode.center,), 1),
                    repeat(formats,)
                ),
                chain((u' ',), repeat(u'-', 1), repeat(u' ')),
                chain((u'|', u'+'), repeat(u'|'))
            )
        ] + [strip,])
    ]

    if footer:
        footers = iterable(footer)
        footer = [ strip ] + \
                 [ u'|%s|' % balign(f, length-1) for f in footers ] + \
                 [ strip, u'' ]
        out.append(u'\n'.join(footer))

    l = u'\n'.join(out)
    if l[-1] != u'\n':
        l = l + u'\n'
    output.write(l)


def render_rst_grid(rows, **kwds):
    output  = kwds.get('output', sys.stdout)
    formats = kwds.get('formats')
    special = kwds.get('special')
    rows = list(rows)
    if not formats:
        formats = lambda: chain((str.ljust,), repeat(str.rjust))

    cols = len(rows[0])
    paddings = [
        max([len(str(r[i])) for r in rows]) + 2
            for i in xrange(cols)
    ]

    length = sum(paddings) + cols
    strip = '+%s+' % ('-' * (length-1))
    out = list()
    if banner:
        lines = iterable(banner)
        banner = [ strip ] + \
                 [ '|%s|' % balign(l, length-1) for l in lines ] + \
                 [ strip, ]
        out.append('\n'.join(banner))

    rows.insert(1, [ '-', ] * cols)
    out += [
        '\n'.join([
            k + '|'.join([
                fmt(str(column), padding, (
                    special if column == special else fill
                )) for (column, fmt, padding) in zip(row, fmts(), paddings)
            ]) + k for (row, fmts, fill, k) in zip(
                rows,
                chain(
                    repeat(lambda: repeat(str.center,), 1),
                    repeat(formats,)
                ),
                chain((' ',), repeat('-', 1), repeat(' ')),
                chain(('|', '+'), repeat('|'))
            )
        ] + [strip,])
    ]

    if footer:
        footers = iterable(footer)
        footer = [ strip ] + \
                 [ '|%s|' % balign(f, length-1) for f in footers ] + \
                 [ strip, '' ]
        out.append('\n'.join(footer))

    output.write(add_linesep_if_missing('\n'.join(out)))

def bits_table(bits=64, **kwds):

    k = Dict(kwds)
    k.banner = ('Bits', '(%d-bit)' % bits)
    k.formats = lambda: chain(
        (str.ljust, str.center,),
        (str.rjust, str.rjust,),
        (str.ljust, str.center),
    )

    rows = [('2^n', '%d-n' % bits, 'Int', 'Size', 'Hex', 'Bin')]

    for i in range(1, bits+1):
        v = 2 ** i
        rows.append([
            '2^%d' % i,
            str(bits - i),
            str(int(v)),
            bytes_to_human(v).replace('.0', ''),
            hex_zfill(v),
            bin_zfill(v),
        ])

    render_text_table(rows, **k)

def bits_table2(bits=64):

    k = Dict()
    k.banner = ('Bits', '(%d-bit)' % bits)
    k.formats = lambda: chain(
        (str.ljust, str.center,),
        (str.rjust, str.rjust,),
        (str.ljust,),
        (str.center,)
    )

    rows = [('2^n', '%d-n' % bits, 'Int', 'Size', 'Hex', 'Bin')]

    for i in range(1, bits+1):
        v = 2 ** i
        rows.append([
            '2^%d-1' % i,
            ' ',
            str(int(v-1)),
            bytes_to_human(v-1).replace('.0', ''),
            hex_zfill(v-1),
            bin_zfill(v-1),
        ])
        rows.append([
            '2^%d' % i,
            str(bits - i),
            str(int(v)),
            bytes_to_human(v).replace('.0', ''),
            hex_zfill(v),
            bin_zfill(v),
        ])

    render_text_table(rows, **k)

def bits_table3(bits=64):

    k = Dict()
    k.banner = ('Bits', '(%d-bit)' % bits)
    k.formats = lambda: chain(
        (str.ljust, str.rjust,),
        (str.rjust, str.rjust,),
        (str.ljust,),
    )

    rows = [('2^n-1', 'Int', 'Size', 'Hex', 'Bin')]

    for i in range(1, bits+1):
        v = (2 ** i)-1
        rows.append([
            '2^%d-1' % i,
            str(int(v)),
            bytes_to_human(v).replace('.0', ''),
            hex_zfill(v),
            bin_zfill(v),
        ])

    render_text_table(rows, **k)


def literal_eval(v):
    try:
        import ast
    except ImportError:
        return eval(v)
    else:
        return ast.literal_eval(v)

def load_propval(orig_value, propname, attempts):
    c = itertools.count(0)

    eval_value = None
    conv_value = None

    last_attempt = False

    attempt = attempts.next()

    try:
        if attempt == c.next():
            assert orig_value == literal_eval(orig_value)
            return orig_value

        if attempt == c.next():
            conv_value = pformat(orig_value)
            eval_value = literal_eval(conv_value)
            assert eval_value == orig_value
            return conv_value

        if attempt == c.next():
            conv_value = '"""%s"""' % pformat(orig_value)
            eval_value = literal_eval(conv_value)
            assert eval_value == orig_value
            return conv_value

        if attempt == c.next():
            conv_value = repr(orig_value)
            eval_value = literal_eval(conv_value)
            assert eval_value == orig_value
            return conv_value

        if attempt == c.next():
            conv_value = str(orig_value)
            eval_value = literal_eval(conv_value)
            assert eval_value == orig_value
            return conv_value

        last_attempt = True

    except:
        if not last_attempt:
            return load_propval(orig_value, propname, attempts)
        else:
            raise ValueError(
                "failed to convert property '%s' value: %s" % (
                    propname,
                    orig_value,
                )
            )

def get_methods_in_order(obj, predicate=None):
    """
    Return a tuple consisting of two-pair tuples.  The first value is an
    integer starting at 0 and the second is the value of the method name.

    If predicate is not None, predicate(method_name) will be called with
    the method name (string).  Return True to add the value to the list.

    >>> class Test(object):
    ...     def __init__(self): pass
    ...     def xyz(self): pass
    ...     def abc(self): pass
    ...     def kef(self): pass
    >>>
    >>> t = Test()
    >>> get_methods_in_order(t)
    ((0, 'xyz'), (1, 'abc'), (2, 'kef'))
    >>> [ n for n in dir(t) if n[0] != '_' ]
    ['abc', 'kef', 'xyz']
    >>>

    >>> class PredicateTest(object):
    ...     def f_z(self): pass
    ...     def xyz(self): pass
    ...     def f_x(self): pass
    ...     def abc(self): pass
    ...     def f_a(self): pass
    ...     def kef(self): pass
    >>>
    >>> t = PredicateTest()
    >>> get_methods_in_order(t, lambda s: s.startswith('f_'))
    ((0, 'f_z'), (1, 'f_x'), (2, 'f_a'))
    >>> [ n for n in dir(t) if n[0] != '_' ]
    ['abc', 'f_a', 'f_x', 'f_z', 'kef', 'xyz']
    >>>
    """
    return tuple(
        (i, m) for (i, m) in enumerate(
              m[1] for m in sorted(
                  (m[1].im_func.func_code.co_firstlineno, m[0]) for m in (
                      inspect.getmembers(obj, lambda v:
                          inspect.ismethod(v) and
                          v.im_func.func_name[0] != '_'
                      )
                  )
              ) if not predicate or predicate(m[1])
        )
    )


def get_source(obj):
    src = None
    try:
        src = inspect.getsource(obj)
    except (TypeError, IOError):
        pass

    if src:
        return src

    try:
        from IPython.core import oinspect
    except ImportError:
        pass
    else:
        try:
            src = oinspect.getsource(obj)
        except TypeError:
            pass

    if src:
        return src

    main = sys.modules['__main__']
    pattern = re.compile('class %s\(' % obj.__class__.__name__)
    for src in reversed(main.In):
        if pattern.search(src):
            return src

def timestamp():
    return datetime.datetime.now()

def timestamp_string(strftime='%Y%m%d%H%M%S-%f'):
    return datetime.datetime.now().strftime(strftime)

def friendly_timedelta(td):
    parts = []
    s = str(td)
    ix = s.find(',')
    if ix != -1:
        parts.append(s[:ix])
        hhmmss = s[ix+2:]
    else:
        hhmmss = s

    values = (hh, mm, ss) = [ v.lstrip('0') for v in hhmmss.split(':') ]
    names = ('hours', 'minutes', 'seconds')
    for (value, name) in zip(values, names):
        if not value:
            continue
        if value == '1':
            # Make singular
            name = name[:-1]
        parts.append('%s %s' % (value, name))

    return ', '.join(parts)

def touch_file(path):
    if os.path.exists(path):
        return

    with open(path, 'w') as f:
        f.truncate(0)
        f.flush()
        f.close()

    assert os.path.exists(path)

def try_remove_file(path):
    try:
        os.unlink(path)
    except:
        pass

def try_remove_file_atexit(path):
    import atexit
    atexit.register(try_remove_file, path)

def try_remove_dir(path):
    shutil.rmtree(path, ignore_errors=True)

def try_remove_dir_atexit(path):
    import atexit
    atexit.register(try_remove_dir, path)

def pid_exists(pid):
    if os.name == 'nt':
        import psutil
        return psutil.pid_exists(pid)
    else:
        try:
            os.kill(pid, 0)
        except OSError as e:
            import errno
            if e.errno == errno.ESRCH:
                return False
            else:
                raise
        else:
            return True

def get_week_bounds_for_day(weeks_from_day=0, day=None):
    """
    Return a tuple consisting of two datetime.date() values that represent
    the first day of the week (Monday) and last day of the week (Sunday)
    based on the input parameters ``weeks_from_day`` and ``day``.

    By default, if no values are provided, the bounds for the week of the
    current day are returned.  ``weeks_from_day`` would be 0 in this case.
    A value of 1 would return the bounds for next week from the current day.

    If a value is provided for ``day``, it will be used instead of today's
    date.  (This was mainly added to assist writing static doctests below,
    but it may be helpful in certain situations.)

    Tests against a mid-week day, including a month and year transition:
        >>> day = datetime.date(2013, 07, 20)
        >>> get_week_bounds_for_day(day=day)
        (datetime.date(2013, 7, 15), datetime.date(2013, 7, 21))
        >>> get_week_bounds_for_day(weeks_from_day=1, day=day)
        (datetime.date(2013, 7, 22), datetime.date(2013, 7, 28))
        >>> get_week_bounds_for_day(weeks_from_day=2, day=day)
        (datetime.date(2013, 7, 29), datetime.date(2013, 8, 4))

        >>> day = datetime.date(2013, 12, 31)
        >>> get_week_bounds_for_day(day=day)
        (datetime.date(2013, 12, 30), datetime.date(2014, 1, 5))
        >>> get_week_bounds_for_day(weeks_from_day=1, day=day)
        (datetime.date(2014, 1, 6), datetime.date(2014, 1, 12))

    Tests against a start-of-week day:
        >>> day = datetime.date(2013, 12, 30)
        >>> get_week_bounds_for_day(day=day)
        (datetime.date(2013, 12, 30), datetime.date(2014, 1, 5))
        >>> get_week_bounds_for_day(weeks_from_day=1, day=day)
        (datetime.date(2014, 1, 6), datetime.date(2014, 1, 12))

    Tests against a end-of-week day:
        >>> day = datetime.date(2014, 2, 2)
        >>> get_week_bounds_for_day(day=day)
        (datetime.date(2014, 1, 27), datetime.date(2014, 2, 2))

    """
    if not day:
        day = datetime.date.today()

    if weeks_from_day:
        day = day + datetime.timedelta(weeks=weeks_from_day)

    day_of_week = calendar.weekday(day.year, day.month, day.day)

    monday = day - datetime.timedelta(days=day_of_week)
    sunday = day + datetime.timedelta(days=(6 - day_of_week))

    return (monday, sunday)

def get_days_between_dates(start_date, end_date):
    """
    Returns a list of datetime.date objects between start_date and end_date.
    """
    days = list()
    next_date = start_date
    while True:
        days.append(next_date)
        next_date = next_date + datetime.timedelta(days=1)
        if next_date > end_date:
            break
    return days

def get_days_for_year(years):
    cal = calendar.Calendar()
    return [
        (year, month, day)
            for year in years
                for month in range(1, 13)
                    for day in cal.itermonthdays(year, month)
                        if day
    ]

def get_days_for_year_dd_MMM_yyyy(years):
    return [
         (year, month, day, '%s-%s-%d' % (
            str(day).zfill(2),
            SHORT_MONTHS_UPPER[month-1][:3],
            year,
        )) for (year, month, day) in iterdays(years)
    ]

def clear_screen():
    if os.name == 'nt':
        os.system('cls')
    else:
        sys.stdout.write(chr(27) + "[2J")

def rotate_file(path, zfill_digits=5):
    """
    Rotate a file by renaming it to a new name with a sequential number
    injected.  The new name will be the original basename (i.e. excluding
    `.<extension>`, followed by an underscore, and then a zero-padded number.
    The number of digits to pad with is specified by `zfill_digits`.  The
    routine will start at 1 and increment until it finds a filename that does
    not exist.

    If no free file can be found based on `zfill_digits`, the routine will
    add an additional digit to `zfill_digits` and try again.
    """
    (prefix, ext) = splitext(path)
    base = basename(prefix)
    exists = os.path.exists
    dname = dirname(path)
    from .path import join_path
    while True:
        for i in itertools.count(1):
            new_filename = f'{base}_{str(i).zfill(zfill_digits)}{ext}'
            new_path = join_path(dname, new_filename)
            if not exists(new_path):
                os.rename(path, new_path)
                return new_path

        zfill_digits += 1

# memoize/memoized lovingly stolen from conda.utils.
class memoized(object):
    """Decorator. Caches a function's return value each time it is called.
    If called later with the same arguments, the cached value is returned
    (not reevaluated).
    """
    def __init__(self, func):
        self.func = func
        self.cache = {}
    def __call__(self, *args):
        if not isinstance(args, collections.Hashable):
            # uncacheable. a list, for instance.
            # better to not cache than blow up.
            return self.func(*args)
        if args in self.cache:
            return self.cache[args]
        else:
            value = self.func(*args)
            self.cache[args] = value
            return value

class memoize(object): # 577452
    def __init__(self, func):
        self.func = func
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self.func
        return partial(self, obj)
    def __call__(self, *args, **kw):
        obj = args[0]
        try:
            cache = obj.__cache
        except AttributeError:
            cache = obj.__cache = {}
        key = (self.func, args[1:], frozenset(kw.items()))
        try:
            res = cache[key]
        except KeyError:
            res = cache[key] = self.func(*args, **kw)
        return res

def list_zfill(l, width):
    """
    Pad a list with empty strings on the left, to fill the list to the
    specified width.  No-op when len(l) >= width.

    >>> list_zfill(['a', 'b'], 5)
    ['', '', '', 'a', 'b']
    >>> list_zfill(['a', 'b', 'c'], 1)
    ['a', 'b', 'c']
    >>> list_zfill(['a', 'b', 'c'], 3)
    ['a', 'b', 'c']
    """
    list_len = len(l)
    if len(l) >= width:
        return l

    return [ '' for _ in range(0, width-list_len) ] + l

class timer:
    """
    Helper class for timing execution of code within a code block.
    Usage:

    > with timer.timeit():
        ...
        ...
    135ms
    """
    def __init__(self, verbose=False):
        self.start = None
        self.stop = None
        self.elapsed = None
        self.nsec = None
        self.msec = None
        self.mill = None
        self.fmt = None
        self.verbose = verbose

    def __str__(self):
        return self.fmt

    def __repr__(self):
        return self.fmt

    def __enter__(self):
        self.start = time.clock()

    def __exit__(self, *exc_info):
        self.stop = time.clock()
        self.elapsed = self.stop - self.start
        self.nsec = self.elapsed * 1e9
        self.msec = self.elapsed * 1e6
        self.mill = self.elapsed * 1e3
        if self.nsec < 1000:
            self.fmt = "%dns" % self.nsec
        elif self.msec < 1000:
            self.fmt = "%dus" % self.msec
        elif self.mill < 1000:
            self.fmt = "%dms" % self.mill
        else:
            self.fmt = "%0.3fs" % self.elapsed

        if self.verbose:
            print(self.fmt)

    @classmethod
    def timeit(cls):
        return cls(verbose=True)

def archive_untracked_git_files(path, archive_path):
    from .path import join_path
    with chdir(path):
        args = ['git', 'status', '--porcelain', '--untracked-files=all']
        result = subprocess.run(args, stdout=PIPE, text=True)

        output = result.stdout.split('\n')

        lines = [ l[3:].strip('"') for l in output if l.startswith('??') ]

        dirname = os.path.dirname

        for line in lines:
            src_path = join_path('.', line)
            dst_path = join_path(archive_path, line)
            os.makedirs(dirname(dst_path), exist_ok=True)
            shutil.move(src_path, dst_path)
            print(f'Moved {src_path} to {dst_path}')


#===============================================================================
# Helper Classes
#===============================================================================

class NullObject(object):
    """
    This is a helper class that does its best to pretend to be forgivingly
    null-like.

    >>> n = NullObject()
    >>> n
    None
    >>> n.foo
    None
    >>> n.foo.bar.moo
    None
    >>> n.foo().bar.moo(True).cat().hello(False, abc=123)
    None
    >>> n.hornet(afterburner=True).shotdown(by=n().tomcat)
    None
    >>> n or 1
    1
    >>> str(n)
    ''
    >>> int(n)
    0
    >>> len(n)
    0
    """
    def __getattr__(self, name):
        return self

    def __getitem__(self, item):
        return self

    def __call__(self, *args, **kwds):
        return self

    def __nonzero__(self):
        return False

    def __repr__(self):
        return repr(None)

    def __str__(self):
        return ''

    def __int__(self):
        return 0

    def __len__(self):
        return 0

class forgiving_list(list):
    """
    Helper class that returns None upon __getitem__ index errors.
    (``forgiving_list`` is a terrible name for this class.)

    >>> l = forgiving_list(['a', 'b'])
    >>> [ l[i] for i in range(0, len(l)+2) ]
    ['a', 'b', None, None]
    >>> l[3]
    >>>
    >>> l[-100]
    >>>
    """

    def __init__(self, seq):
        self.seq = seq
        list.__init__(self, seq)

    def __getitem__(self, i):
        try:
            return list.__getitem__(self, i)
        except IndexError:
            return None

class word_groups(object):
    """
    >>> l = word_groups(['a', 'b', 'c', 'd'], size=2)
    >>> l[0]
    ['a', 'b']
    >>> l[1]
    ['b', 'c']
    >>> l[2]
    ['c', 'd']
    >>> l[3]
    ['d', None]
    >>> l[4]
    [None, None]
    >>> l[100]
    [None, None]
    >>> [ e for e in l ]
    [['a', 'b'], ['b', 'c'], ['c', 'd'], ['d']]
    """
    def __init__(self, seq, size=2):
        if not isinstance(seq, list):
            seq = seq.split(' ')
        self.seq = forgiving_list(seq)
        self.size = size

    def __getitem__(self, i):
        l = self.seq
        m = i + self.size
        return [ l[x] for x in range(i, m) ]

    def __iter__(self):
        i = 0
        while True:
            r = [ e for e in self[i] if e ]
            if not r:
                raise StopIteration
            yield r
            i += 1

    def __repr__(self):
        return repr([ e for e in self ])

class before_and_after(object):
    """
    >>> l = before_and_after(['a', 'b', 'c', 'd'])
    >>> l[0]
    ('a', None, 'b')
    >>> l[1]
    ('b', 'a', 'c')
    >>> l[2]
    ('c', 'b', 'd')
    >>> l[3]
    ('d', 'c', None)
    >>> l[4]
    (None, None, None)
    >>> [ e for e in l ]
    [('a', None, 'b'), ('b', 'a', 'c'), ('c', 'b', 'd'), ('d', 'c', None)]
    """
    def __init__(self, seq):
        if not isinstance(seq, list):
            seq = seq.split(' ')
        self.seq = forgiving_list(seq)

    def __getitem__(self, i):
        l = self.seq
        if i < 0:
            return (None, None, None)
        elif i >= len(l):
            return (None, None, None)
        prev = l[i-1] if i > 0 else None
        next = l[i+1] if i < len(l)+1 else None
        return (l[i], prev, next)

    def __iter__(self):
        i = 0
        while True:
            #r = [e for e in self[i]]
            r = self[i]
            if r == (None, None, None):
                raise StopIteration
            yield r
            i += 1

    def __repr__(self):
        return repr([ e for e in self ])

class chdir(object):
    def __init__(self, path):
        self.old_path = os.getcwd()
        self.path = path

    def __enter__(self):
        os.chdir(self.path)
        return self

    def __exit__(self, *exc_info):
        os.chdir(self.old_path)

class SlotObject(object):
    # Subclasses need to define __slots__
    _default_ = None
    _defaults_ = dict()

    _to_dict_prefix_ = ''
    _to_dict_suffix_ = ''
    _to_dict_exclude_ = set()
    # If set to True, automatically exclude any slots with None values.
    _to_dict_exclude_none_values_ = False

    # Defaults to _to_dict_exclude_ if not set.
    _repr_exclude_ = set()

    def __init__(self, *args, **kwds):
        seen = set()
        slots = list(self.__slots__)
        args = [ a for a in args ]
        while args:
            (key, value) = (slots.pop(0), args.pop(0))
            seen.add(key)
            setattr(self, key, value)

        for (key, value) in kwds.items():
            seen.add(key)
            setattr(self, key, value)

        for slot in self.__slots__:
            if slot not in seen:
                if slot in self._defaults_:
                    default = copy.deepcopy(self._defaults_[slot])
                else:
                    default = copy.deepcopy(self._default_)
                setattr(self, slot, default)

        return

    def _to_dict(self, prefix=None, suffix=None, exclude=None):
        prefix = prefix or self._to_dict_prefix_
        suffix = suffix or self._to_dict_suffix_
        exclude = exclude or self._to_dict_exclude_
        d = {
            f'{prefix}{key}{suffix}': getattr(self, key)
                for key in self.__slots__
                    if key not in exclude
        }
        if self._to_dict_exclude_none_values_:
            d = { k: v for (k, v) in d.items() if v is not None }
        return d

    def __repr__(self):
        slots = self.__slots__
        exclude = self._repr_exclude_ or self._to_dict_exclude_

        q = lambda v: v if (not v or isinstance(v, int)) else '"%s"' % v
        return "<%s %s>" % (
            self.__class__.__name__,
            ', '.join(
                '%s=%s' % (k, q(v))
                    for (k, v) in (
                        (k, getattr(self, k))
                            for k in slots
                                if k not in exclude
                    )
                )
        )

    @property
    def sha256(self):
        """Compute a SHA256 checksum of all key-value pairs in the dictionary."""
        hasher = hashlib.sha256()
        # Sort the keys to ensure consistent order
        sorted_items = sorted(self._to_dict().items())
        # Create a consistent string representation of the dictionary
        encoded_items = str(sorted_items).encode()
        # Update the hash with this byte string
        hasher.update(encoded_items)
        # Return the hexadecimal string representation of the hash
        return hasher.hexdigest()

    @property
    def sha256_path(self):
        """
        Return a path-based SHA256 checksum similar to git's object storage.
        The first two characters of the checksum are used as a directory,
        and the remaining characters are used as the filename.
        """
        checksum = self.sha256
        return f'{checksum[:2]}/{checksum[2:]}'

    def __hash__(self):
        """Override the hash function to use the SHA256 checksum."""
        # Convert the hex digest to an integer
        return int(self.sha256, 16)

class UnexpectedCodePath(RuntimeError):
    pass

class ContextSensitiveObject(object):
    allow_reentry_after_exit = True

    def __init__(self, *args, **kwds):
        self.context_depth = 0
        self.entered = False
        self.exited = False

    def __enter__(self):
        assert self.entered is False
        if self.allow_reentry_after_exit:
            self.exited = False
        else:
            assert self.exited is False
        result = self._enter()
        self.entered = True
        assert isinstance(result, self.__class__)
        return result

    def __exit__(self, *exc_info):
        assert self.entered is True and self.exited is False
        self._exit()
        self.exited = True
        self.entered = False

    def _enter(self):
        raise NotImplementedError

    def _exit(self, *exc_info):
        raise NotImplementedError

class ImplicitContextSensitiveObject(object):

    def __init__(self, *args, **kwds):
        self.context_depth = 0

    def __enter__(self):
        self.context_depth += 1
        self._enter()
        return self

    def __exit__(self, *exc_info):
        self.context_depth -= 1
        self._exit(*exc_info)

    def _enter(self):
        raise NotImplementedError

    def _exit(self, *exc_info):
        raise NotImplementedError

class ConfigList(list):
    def __init__(self, parent, name, args):
        self._parent = parent
        self._name = name
        list.__init__(self, args)

    def append(self, value):
        list.append(self, value)
        self._parent._save(self._name, self)

class ConfigDict(dict):
    def __init__(self, parent, name, kwds):
        self._parent = parent
        self._name = name
        dict.__init__(self, kwds)

    def __getattr__(self, name):
        if name[0] == '_':
            return dict.__getattribute__(self, name)
        else:
            return self.__getitem__(name)

    def __setattr__(self, name, value):
        if name[0] == '_':
            dict.__setattr__(self, name, value)
        else:
            self.__setitem__(name, value)

    def __getitem__(self, name):
        i = dict.__getitem__(self, name)
        if isinstance(i, dict):
            return ConfigDict(self, name, i)
        elif isinstance(i, list):
            return ConfigList(self, name, i)
        else:
            return i

    def __delitem__(self, name):
        dict.__delitem__(self, name)
        self._parent._save(self._name, self)

    def __setitem__(self, name, value):
        dict.__setitem__(self, name, value)
        self._parent._save(self._name, self)

    def _save(self, name, value):
        self[name] = value


class Options(dict):
    def __init__(self, values=dict()):
        assert isinstance(values, dict)
        dict.__init__(self, **values)

    def __getattr__(self, name):
        if name not in self:
            return False
        else:
            return self.__getitem__(name)

#===============================================================================
# Helper Classes
#===============================================================================
class Constant(dict):
    def __init__(self):
        items = self.__class__.__dict__.items()
        filtered = filter(lambda t: t[0][:2] != '__', items)
        for (key, value) in filtered:
            try:
                self[value] = key
                if isinstance(key, str) and isinstance(value, int):
                    self[str(value)] = key
            except:
                pass

        for (key, value) in filtered:
            l = key.lower()
            if l not in self:
                self[l] = value

            u = key.upper()
            if u not in self:
                self[u] = value

    def __getattr__(self, name):
        return self.__getitem__(name)

def invert_counts(d, sort=True, reverse=True):
    i = {}
    for (k, v) in d.items():
        if isinstance(k, str):
            if k[0] == '_' or k == 'trait_names':
                continue
        i.setdefault(v, []).append(k)
    if not sort:
        return i
    else:
        keys = [ k for k in sorted(i.keys(), reverse=reverse) ]
        return [ (key, value) for key in keys for value in i[key] ]

class Stats(defaultdict):
    def __init__(self, typename=int):
        defaultdict.__init__(self, typename)

    def __getattr__(self, name):
        return self.__getitem__(name)

    def __setattr__(self, name, value):
        return self.__setitem__(name, value)

    def keys(self):
        return [
            k for k in defaultdict.keys(self) if (
                not isinstance(k, str) or
                k[0] != '_' and k != 'trait_names'
            )
        ]

    def _to_dict(self):
        return { k: self[k] for k in self.keys() }

    def _to_json(self):
        return json.dumps(self)

    def _save(self, path):
        with open(path, 'w') as f:
            json.dump(f, self)

    def _invert(self):
        return invert_counts(self)

    def merge(self, other):
        for (k, v) in other.items():
            self[k] += v

class KeyedStats(Stats):
    def __init__(self):
        Stats.__init__(self, typename=lambda: Stats())

    def _invert(self):
        return { k: self[k]._invert() for k in self.keys() }

class Dict(dict):
    """
    A dict that allows direct attribute access to keys.
    """
    def __init__(self, *args, **kwds):
        dict.__init__(self, *args, **kwds)
    def __getattr__(self, name):
        return self.__getitem__(name)
    def __setattr__(self, name, value):
        return self.__setitem__(name, value)

    @property
    def sha256(self):
        """Compute a SHA256 checksum of all key-value pairs in the dictionary."""
        hasher = hashlib.sha256()
        # Sort the keys to ensure consistent order
        sorted_items = sorted(self.items())
        # Create a consistent string representation of the dictionary
        encoded_items = str(sorted_items).encode()
        # Update the hash with this byte string
        hasher.update(encoded_items)
        # Return the hexadecimal string representation of the hash
        return hasher.hexdigest()

    def __hash__(self):
        """Override the hash function to use the SHA256 checksum."""
        # Convert the hex digest to an integer
        return int(self.sha256, 16)

class ForgivingDict(Dict):
    """
    A dict that returns None for missing keys.
    """
    def __getitem__(self, name):
        return dict.get(self, name, None)

class DecayDict(Dict):
    """
    A dict that allows once-off direct attribute access to keys.  The key/
    attribute is subsequently deleted after a successful get.
    """
    def __getitem__(self, name):
        v = dict.__getitem__(self, name)
        del self[name]
        return v

    def get(self, name, default=None):
        v = dict.get(self, name, default)
        if name in self:
            del self[name]
        return v

    def __getattr__(self, name):
        return self.__getitem__(name)
    def __setattr__(self, name, value):
        return self.__setitem__(name, value)

    def assert_empty(self, obj):
        if self:
            raise RuntimeError(
                "%s:%s: unexpected keywords: %s" % (
                    obj.__class__.__name__,
                    inspect.currentframe().f_back.f_code.co_name,
                    repr(self)
                )
            )

class ProcessWrapper(object):
    def __init__(self, exe, *args, **kwds):
        self.exe      = exe
        self.rc       = int()
        self.cwd      = None
        self.wait     = True
        self.error    = str()
        self.output   = str()
        self.ostream  = kwds.get('ostream', sys.stdout)
        self.estream  = kwds.get('estream', sys.stderr)
        self.verbose  = kwds.get('verbose', False)
        self.safe_cmd = None
        self.exception_class = RuntimeError
        self.raise_exception_on_error = True

    def __getattr__(self, attr):
        if not attr.startswith('_') and not attr == 'trait_names':
            return lambda *args, **kwds: self.execute(attr, *args, **kwds)
        else:
            raise AttributeError(attr)

    def __call__(self, *args, **kwds):
        return self.execute(*args, **kwds)

    def build_command_line(self, exe, action, *args, **kwds):
        cmd  = [ exe, action ]
        for (k, v) in kwds.items():
            cmd.append(
                '-%s%s' % (
                    '-' if len(k) > 1 else '', k.replace('_', '-')
                )
            )
            if not isinstance(v, bool):
                cmd.append(v)
        cmd += list(args)
        return cmd

    def kill(self):
        self.p.kill()

    def execute(self, *args, **kwds):
        self.rc = 0
        self.error = ''
        self.output = ''

        self.cmd = self.build_command_line(self.exe, *args, **kwds)

        if self.verbose:
            cwd = self.cwd or os.getcwd()
            cmd = ' '.join(self.safe_cmd or self.cmd)
            self.ostream.write('%s>%s\n' % (cwd, cmd))

        self.p = Popen(self.cmd, executable=self.exe, cwd=self.cwd,
                       stdin=PIPE, stdout=PIPE, stderr=PIPE)
        if not self.wait:
            return

        self.outbuf = StringIO.StringIO()
        self.errbuf = StringIO.StringIO()

        while self.p.poll() is None:
            out = self.p.stdout.read().decode('utf-8')
            self.outbuf.write(out)
            if self.verbose and out:
                self.ostream.write(out)

            err = self.p.stderr.read().decode('utf-8')
            self.errbuf.write(err)
            if self.verbose and err:
                self.estream.write(err)

        self.rc = self.p.returncode
        self.error = self.errbuf.getvalue()
        self.output = self.outbuf.getvalue()
        if self.rc != 0 and self.raise_exception_on_error:
            if self.error:
                error = self.error
            elif self.output:
                error = 'no error info available, output:\n' + self.output
            else:
                error = 'no error info available'
            printable_cmd = ' '.join(self.safe_cmd or self.cmd)
            raise self.exception_class(printable_cmd, error)
        if self.output and self.output.endswith('\n'):
            self.output = self.output[:-1]

        return self.process_output(self.output)

    def process_output(self, output):
        return output

    def clone(self):
        return self.__class__(self.exe)

#===============================================================================
# dd helper
#===============================================================================
class Dd(SlotObject):
    __slots__ = [
        'bs',
        'skip',
        'seek',
        'count',
        'skipped_bytes',
        'seeked_bytes',
        'total_bytes',
    ]
    def __init__(self, bs, skip, seek, count):
        self.bs = int(bs)
        self.skip = int(skip)
        self.seek = int(seek)
        self.count = int(count)
        self.skipped_bytes = self.skip * self.count
        self.seeked_bytes = self.seek * self.count
        self.total_bytes = self.bs * self.count

    @classmethod
    def slice_blocks(cls, size, count):
        from math import floor
        block_size = floor(size / count)
        remainder = size - (block_size * count)
        blocks = [ block_size for _ in range(count) ]
        blocks[-1] += remainder
        return blocks

    @classmethod
    def get_dds(cls, total_bytes, num_procs, block_size=65536,
                min_block_size=4096):
        assert min_block_size < block_size, (min_block_size, block_size)
        assert min_block_size > 0, (min_block_size)
        assert is_power_of_2(min_block_size), (min_block_size)
        assert block_size % min_block_size == 0

        remaining_bytes = total_bytes % block_size
        parallel_bytes = total_bytes - remaining_bytes

        is_perfect_fit = (remaining_bytes == 0)
        if is_perfect_fit:
            actual_procs = num_procs
            remaining_block_count = 0
            remaining_block_multiplier = 0
        else:
            actual_procs = num_procs + 1
            assert remaining_bytes % min_block_size == 0, (
                remaining_bytes % min_block_size
            )
            remaining_block_count = remaining_bytes / min_block_size
            remaining_block_multiplier = block_size / min_block_size

        assert actual_procs >= 1, actual_procs

        parallel_block_count = parallel_bytes / block_size
        slices = cls.slice_blocks(parallel_block_count, num_procs)
        assert len(slices) == num_procs, (len(slices), num_procs)

        dds = list()
        start = 0
        end = 0
        for (i, slice) in enumerate(slices):
            if i == 0:
                offset = 0
            else:
                offset = sum(slices[:i])
            count = slices[i]
            dd = Dd(
                bs=block_size,
                skip=offset,
                seek=offset,
                count=count,
            )
            dds.append(dd)

        if not is_perfect_fit:
            offset = sum(slices)
            dd = Dd(
                bs=min_block_size,
                skip=offset,
                seek=offset,
                count=remaining_block_count
            )
            dds.append(dd)

        total_check = sum(dd.total_bytes for dd in dds)
        assert total_bytes == total_check, (total_bytes, total_check)

        return dds

    @classmethod
    def convert_dd_to_command(cls, dd, input_file, output_file):
        cmd = (
            f'dd if={input_file} of={output_file} '
            f'bs={dd.bs} skip={dd.skip} seek={dd.seek} '
            f'count={dd.count} status=progress &'
        )
        return cmd

def dds_example():
    size = 1024209543168
    dds = Dd.get_dds(size, 12)
    cmds = [
        Dd.convert_dd_to_command(
            dd,
            '/dev/nvd1',
            '/dev/nvd0',
        ) for dd in dds
    ]
    text = '#!/bin/sh\n\n' + '\n'.join(cmds)
    print(text)
    return text


#===============================================================================
# CSV Tools/Utils
#===============================================================================
def create_namedtuple(name, data, mutable=False):
    header = list()
    wrappers = list()
    first = data.pop(0)
    # Skip over any empty columns.
    columns = [ c for c in first if c ]
    for col in columns:
        if '|' not in col:
            wrappers.append(None)
            header.append(col)
        else:
            import __builtin__
            (colname, classname) = col.split('|')
            if '.' in classname:
                assert classname.count('.') == 1
                (module, classname) = classname.split('.')
                cls = getattr(sys.modules[module], classname)
            elif classname.startswith('timestamp'):
                from datetime import datetime
                cls = lambda d: datetime.strptime(d, classname.split(',')[1])
            elif hasattr(__builtin__, classname):
                cls = getattr(__builtin__, classname)
            else:
                cls = globals()[classname]
            wrappers.append(cls)
            header.append(colname)

    rows = list()
    num_cols = len(header)
    for columns in data:
        if not isinstance(columns, list):
            columns = list(columns)
        l = logic.Mutex()
        l.correct_columns = num_cols == len(columns)
        l.missing_columns = ((num_cols - len(columns)) > 0)
        l.extra_columns   = ((len(columns) - num_cols) > 0)
        need_other = False
        with l as g:
            if g.correct_columns:
                assert all(isinstance(c, str) for c in columns)
            elif g.missing_columns:
                # Pad our columns list with empty strings.
                columns += ['',] * (num_cols - len(columns))
            elif g.extra_columns:
                # Convert everything past the expected column count to
                # one big list and use that as the 'other' column.
                columns = columns[0:num_cols] + [columns[num_cols:]]
                need_other = True

        if need_other:
            columns.append(list())

        rows.append(columns)

    if need_other:
        header.append('other')
        wrappers.append(None)

    if name.endswith('s'):
        name = name[:-1]

    t = wrappers
    values = list()
    results = list()
    if (all(r == '' for r in rows[-1])):
        rows = rows[:-1]
    values = [
       [ c if not t[i] else t[i](c) for (i, c) in enumerate(row) ]
        for row in rows
    ]
    if not mutable:
        _cls = namedtuple(name, header)
        cls = lambda n, h, v: _cls(*v)
    else:
        cls = lambda n, h, v: type(n, (object,), dict(zip(h, v)))
    results = [
        cls(name, header, v) for v in values
    ]

    return results

def create_namedtuple_from_sequence_of_key_value_pairs(name, seq):
    return create_namedtuple(name, zip(*seq))

def create_namedtuple_from_csv(name, csv):
    l = logic.Mutex()

    l.is_filename = (
        isinstance(csv, str) and
        '\n' not in csv and
        os.path.isfile(csv)
    )

    l.is_csv_text = (
        isinstance(csv, str) and
        '\n' in csv and
        ',' in csv
    )

    l.is_csv_lines = (
        not isinstance(csv, str) and (
            hasattr(csv, '__iter__') or
            hasattr(csv, 'next')
        )
    )

    lines = None

    with l as g:
        if g.is_filename:
            with open(csv, 'r') as f:
                lines = f.read().split('\n')

        elif g.is_csv_text:
            lines = csv.split('\n')

        elif g.is_csv_lines:
            lines = csv

    data = [ r for r in csv_reader(lines) ]
    mutable_sheets = set()
    mutable = True if name in mutable_sheets else False
    return create_namedtuple(name, data, mutable=mutable)

def download_url(url):
    from urllib2 import urlopen
    return urlopen(url).read()

def create_namedtuple_from_csv_url(name, url):
    return create_namedtuple_from_csv(name, download_url(url))

#===============================================================================
# Window Functions
#===============================================================================

if os.name == 'nt':
    def enum_windows():
        from win32gui import GetWindowText, GetClassName, EnumWindows
        results = []
        def _handler(hwnd, results):
            results.append((hwnd, GetWindowText(hwnd), GetClassName(hwnd)))
        EnumWindows(_handler, results)
        return results

    def find_windows(text='', cls=None, windows=None):
        if not windows:
            windows = enum_windows()
        return [
            (h, t, c) for (h, t, c) in windows if (
                text.lower() in t.lower() and (
                    True if not cls else cls == c
                )
            )
        ]

    def find_vim():
        handles = [ w[0] for w in find_windows(cls='Vim') if w[-1] == 'Vim' ]
        return None if not handles else handles[0]

    def make_transparent(hwnd, alpha=232):

        from win32api import (
            RGB,
        )

        from win32con import (
            LWA_ALPHA,
            GWL_EXSTYLE,
            WS_EX_LAYERED,
        )

        from win32gui import (
            SetWindowLong,
            GetWindowLong,
            SetLayeredWindowAttributes,
            GetLayeredWindowAttributes,
        )

        style = GetWindowLong(hwnd, GWL_EXSTYLE)
        style |= WS_EX_LAYERED
        SetWindowLong(hwnd, GWL_EXSTYLE, style)
        SetLayeredWindowAttributes(hwnd, RGB(0,0,0), alpha, LWA_ALPHA)

    def toggle_transparent(hwnd, alpha=232):

        import pywintypes

        from win32api import (
            RGB,
        )

        from win32con import (
            LWA_ALPHA,
            GWL_EXSTYLE,
            WS_EX_LAYERED,
        )

        from win32gui import (
            SetWindowLong,
            GetWindowLong,
            SetLayeredWindowAttributes,
            GetLayeredWindowAttributes,
        )

        is_transparent = False

        # If the window is not transparent, GetLayeredWindowAttributes() will
        # raise an exception.
        try:
            GetLayeredWindowAttributes(hwnd)
            is_transparent = True
        except pywintypes.error as e:
            if e.args[2] != 'The parameter is incorrect.':
                raise

        if is_transparent:
            style = GetWindowLong(hwnd, GWL_EXSTYLE)
            style &= ~WS_EX_LAYERED
            SetWindowLong(hwnd, GWL_EXSTYLE, style)
        else:
            style = GetWindowLong(hwnd, GWL_EXSTYLE)
            style |= WS_EX_LAYERED
            SetWindowLong(hwnd, GWL_EXSTYLE, style)
            SetLayeredWindowAttributes(hwnd, RGB(0,0,0), alpha, LWA_ALPHA)

    def toggle_vim_transparency():
        toggle_transparent(find_vim())

    def apply_window_positions(w):
        from win32gui import SetWindowPlacement
        windows = enum_windows()
        for (text, cls, pos) in w:
            for (h, t, c) in find_windows(text, cls, windows):
                SetWindowPlacement(h, pos)

    def set_window_on_top(text, cls):
        from win32gui import SetWindowPos
        SWP_NOMOVE = 2
        SWP_NOSIZE = 1
        HWND_TOPMOST = -1
        HWND_NOTOPMOST = -2
        flags = SWP_NOMOVE | SWP_NOSIZE
        for (hwnd, wtext, wcls) in enum_windows():
            if wtext.lower().startswith(text.lower()):
                if not cls or wcls.lower().startswith(cls.lower()):
                    print("setting '%s' (%d, %s) on top" % (wtext, hwnd, cls))
                    SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0, flags)

# From: https://code.activestate.com/recipes/577197-sortedcollection/
class SortedCollection(object):
    '''Sequence sorted by a key function.

    SortedCollection() is much easier to work with than using bisect() directly.
    It supports key functions like those use in sorted(), min(), and max().
    The result of the key function call is saved so that keys can be searched
    efficiently.

    Instead of returning an insertion-point which can be hard to interpret, the
    five find-methods return a specific item in the sequence. They can scan for
    exact matches, the last item less-than-or-equal to a key, or the first item
    greater-than-or-equal to a key.

    Once found, an item's ordinal position can be located with the index() method.
    New items can be added with the insert() and insert_right() methods.
    Old items can be deleted with the remove() method.

    The usual sequence methods are provided to support indexing, slicing,
    length lookup, clearing, copying, forward and reverse iteration, contains
    checking, item counts, item removal, and a nice looking repr.

    Finding and indexing are O(log n) operations while iteration and insertion
    are O(n).  The initial sort is O(n log n).

    The key function is stored in the 'key' attibute for easy introspection or
    so that you can assign a new key function (triggering an automatic re-sort).

    In short, the class was designed to handle all of the common use cases for
    bisect but with a simpler API and support for key functions.

    >>> from pprint import pprint
    >>> from operator import itemgetter

    >>> s = SortedCollection(key=itemgetter(2))
    >>> for record in [
    ...         ('roger', 'young', 30),
    ...         ('angela', 'jones', 28),
    ...         ('bill', 'smith', 22),
    ...         ('david', 'thomas', 32)]:
    ...     s.insert(record)

    >>> pprint(list(s))         # show records sorted by age
    [('bill', 'smith', 22),
     ('angela', 'jones', 28),
     ('roger', 'young', 30),
     ('david', 'thomas', 32)]

    >>> s.find_le(29)           # find oldest person aged 29 or younger
    ('angela', 'jones', 28)
    >>> s.find_lt(28)           # find oldest person under 28
    ('bill', 'smith', 22)
    >>> s.find_gt(28)           # find youngest person over 28
    ('roger', 'young', 30)

    >>> r = s.find_ge(32)       # find youngest person aged 32 or older
    >>> s.index(r)              # get the index of their record
    3
    >>> s[3]                    # fetch the record at that index
    ('david', 'thomas', 32)

    >>> s.key = itemgetter(0)   # now sort by first name
    >>> pprint(list(s))
    [('angela', 'jones', 28),
     ('bill', 'smith', 22),
     ('david', 'thomas', 32),
     ('roger', 'young', 30)]

    '''

    def __init__(self, iterable=(), key=None):
        self._given_key = key
        key = (lambda x: x) if key is None else key
        decorated = sorted((key(item), item) for item in iterable)
        self._keys = [k for k, item in decorated]
        self._items = [item for k, item in decorated]
        self._key = key

    def _getkey(self):
        return self._key

    def _setkey(self, key):
        if key is not self._key:
            self.__init__(self._items, key=key)

    def _delkey(self):
        self._setkey(None)

    key = property(_getkey, _setkey, _delkey, 'key function')

    def clear(self):
        self.__init__([], self._key)

    def copy(self):
        return self.__class__(self, self._key)

    def __len__(self):
        return len(self._items)

    def __getitem__(self, i):
        return self._items[i]

    def __iter__(self):
        return iter(self._items)

    def __reversed__(self):
        return reversed(self._items)

    def __repr__(self):
        return '%s(%r, key=%s)' % (
            self.__class__.__name__,
            self._items,
            getattr(self._given_key, '__name__', repr(self._given_key))
        )

    def __reduce__(self):
        return self.__class__, (self._items, self._given_key)

    def __contains__(self, item):
        k = self._key(item)
        i = bisect_left(self._keys, k)
        j = bisect_right(self._keys, k)
        return item in self._items[i:j]

    def index(self, item):
        'Find the position of an item.  Raise ValueError if not found.'
        k = self._key(item)
        i = bisect_left(self._keys, k)
        j = bisect_right(self._keys, k)
        return self._items[i:j].index(item) + i

    def count(self, item):
        'Return number of occurrences of item'
        k = self._key(item)
        i = bisect_left(self._keys, k)
        j = bisect_right(self._keys, k)
        return self._items[i:j].count(item)

    def insert(self, item):
        'Insert a new item.  If equal keys are found, add to the left'
        k = self._key(item)
        i = bisect_left(self._keys, k)
        self._keys.insert(i, k)
        self._items.insert(i, item)

    def insert_right(self, item):
        'Insert a new item.  If equal keys are found, add to the right'
        k = self._key(item)
        i = bisect_right(self._keys, k)
        self._keys.insert(i, k)
        self._items.insert(i, item)

    def remove(self, item):
        'Remove first occurence of item.  Raise ValueError if not found'
        i = self.index(item)
        del self._keys[i]
        del self._items[i]

    def find(self, k):
        'Return first item with a key == k.  Raise ValueError if not found.'
        i = bisect_left(self._keys, k)
        if i != len(self) and self._keys[i] == k:
            return self._items[i]
        raise ValueError('No item found with key equal to: %r' % (k,))

    def find_le(self, k):
        'Return last item with a key <= k.  Raise ValueError if not found.'
        i = bisect_right(self._keys, k)
        if i:
            return self._items[i-1]
        raise ValueError('No item found with key at or below: %r' % (k,))

    def find_lt(self, k):
        'Return last item with a key < k.  Raise ValueError if not found.'
        i = bisect_left(self._keys, k)
        if i:
            return self._items[i-1]
        raise ValueError('No item found with key below: %r' % (k,))

    def find_ge(self, k):
        'Return first item with a key >= equal to k.  Raise ValueError if not found'
        i = bisect_left(self._keys, k)
        if i != len(self):
            return self._items[i]
        raise ValueError('No item found with key at or above: %r' % (k,))

    def find_gt(self, k):
        'Return first item with a key > k.  Raise ValueError if not found'
        i = bisect_right(self._keys, k)
        if i != len(self):
            return self._items[i]
        raise ValueError('No item found with key above: %r' % (k,))


if __name__ == '__main__':
    import doctest
    doctest.testmod()

# vim:set ts=8 sw=4 sts=4 tw=80 et                                             :
