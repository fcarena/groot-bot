from functools import reduce

def getmember(obj, name, default=None):
    if obj is None:
        return default

    if isinstance(obj, dict):
        return obj.get(name, default)

    if isinstance(obj, object):
        return getattr(obj, name, default)

    return default

def getpath(obj, path, default=None):
    return reduce(
        lambda acc, name: getmember(acc, name, default), path.split('.'), obj)

def getpaths(obj, paths, default=None):
    return [getpath(obj, path, default) for path in paths]

def getkeys(obj, keys):
    return dict(zip(keys, getpaths(obj, keys)))
