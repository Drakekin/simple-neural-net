# coding=utf-8
from __future__ import division

BAR = u" ▁▂▃▄▅▆▇█"

def bar(n, min, max):
    return BAR[int(round(((n - min) / (max - min)) * 8))]


def clamp(n, min_value, max_value):
    return max(min(n, max_value), min_value)


def count():
    n = 0
    while True:
        yield n
        n += 1


def chunk(l, n):
    """Yield successive n-sized chunks from l."""
    for i in xrange(0, len(l), n):
        yield l[i:i+n]
