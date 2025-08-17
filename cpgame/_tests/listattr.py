def listattrs(obj, *, public=True, values=False, methods=False, safe=False):
    names = dir(obj)
    if public:
        names = [n for n in names if not n.startswith('_')]
    if methods:
        names = [n for n in names if callable(getattr(obj, n, None))]
    # if values:
    #     getter = inspect.getattr_static if safe else getattr
    #     return {n: getter(obj, n) for n in names}
    return names