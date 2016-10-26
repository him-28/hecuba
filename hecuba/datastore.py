# author: G. Alomar
from hecuba.dict import *
from conf.apppath import apppath
import inspect


def hecuba_filter(function, iterable):
    if hasattr(iterable, 'indexed'):
        inspectedfunction = inspect.getsource(function)
        iterable.indexArguments = str(str(str(inspectedfunction).split(":")[1]).split(",")[0]).split(' and ')  # Args list
        print "iterable.indexArguments:", iterable.indexArguments
        return iterable
    else:
        filtered = python_filter(function, iterable)
        return filtered

path = apppath + '/conf/storage_params.txt'

file = open(path, 'r')

for line in file:
    exec line

if not filter == hecuba_filter:
    python_filter = filter
    filter = hecuba_filter
