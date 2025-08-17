# listattr_demo.py
# Works on MicroPython: no inspect, no f-strings, no __dir__.

try:
    from cpgame.game_data import actors
except ImportError:
    actors = None  # demo still runs; you can replace 'target' manually below.

# One-time debug flags so we don't spam prints
_DEBUG_ONCE = {"mro": False, "inst_dict": False}

def _iter_slots(cls):
    slots = getattr(cls, "__slots__", ())
    if isinstance(slots, str):
        slots = (slots,)
    for s in slots:
        yield s

def _collect_names(obj, include_inherited=True):
    names = set()

    # 1) Instance dictionary (if any)
    d = getattr(obj, "__dict__", None)
    if isinstance(d, dict):
        if not _DEBUG_ONCE["inst_dict"]:
            print("got dict")
            _DEBUG_ONCE["inst_dict"] = True
        for k in d.keys():
            names.add(k)

    # 2) Class dictionaries and slots
    cls = type(obj)

    # Note availability of __mro__ (if present)
    has_mro = getattr(cls, "__mro__", None) is not None
    if has_mro and not _DEBUG_ONCE["mro"]:
        print("got mro")
        _DEBUG_ONCE["mro"] = True

    mro = getattr(cls, "__mro__", (cls,))
    if not include_inherited:
        mro = (cls,)

    for c in mro:
        cd = getattr(c, "__dict__", None)
        if isinstance(cd, dict):
            for k in cd.keys():
                names.add(k)
        for s in _iter_slots(c):
            names.add(s)

    return sorted(names)

def listattr(obj, values=False, include_private=False, include_methods=False, include_inherited=True):
    """
    Return attribute NAMES or (NAME, VALUE) pairs.

    values=False -> list of names
    values=True  -> list of (name, value) via getattr (may trigger properties)
    """
    out = []
    for name in _collect_names(obj, include_inherited=include_inherited):
        if not include_private and name.startswith("_"):
            continue

        if values:
            # Safe getattr: avoid blowing up on descriptors/properties
            try:
                val = getattr(obj, name)
            except Exception:
                continue
            if (not include_methods) and callable(val):
                continue
            out.append((name, val))
        else:
            out.append(name)

    return out

# ---- tiny demo using cpgame.game_data.actors ----
def _pick_target(sample):
    if sample is None:
        return None
    # If it's a dict, take first value; if list/tuple, take first element; else use as-is.
    if isinstance(sample, dict):
        for k in sample:
            return sample[k]
        return None
    if isinstance(sample, (list, tuple)):
        if len(sample) > 0:
            return sample[0]
        return None
    return sample

def demo():
    target = _pick_target(actors)

    if target is None:
        print("Could not load cpgame.game_data.actors; showing a built-in demo object.")
        class Foo(object):
            __slots__ = ("hp", "name")
            kind = "npc"
            def __init__(self):
                self.hp = 10
                self.name = "slime"
            def wave(self):
                return "blob!"
        target = Foo()

    print("Demo target type:", repr(type(target)))

    print("\nPublic data attributes (names + values):")
    for name, val in listattr(target, values=True, include_private=False, include_methods=False)[:12]:
        print(" - %s = %r" % (name, val))

    print("\nAll attribute names (incl. methods & private):")
    for name in listattr(target, values=False, include_private=True, include_methods=True)[:24]:
        print(" - %s" % name)

# Auto-run demo when executed as a script
demo()
