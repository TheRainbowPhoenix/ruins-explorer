# test_udataclasses_extra.py

from udataclasses import (
    MISSING,
    asdict,
    astuple,
    dataclass,
    field,
    fields,
    is_dataclass,
    make_dataclass,
    replace,
)

# 1) is_dataclass
@dataclass
class D:
    a: int = 0

class C:
    a: int = 0

assert is_dataclass(D)
assert not is_dataclass(C)

# 2) fields()
@dataclass
class F:
    a: int = field()
    b: int = field(default=1)

cls_fs = fields(F)
assert len(cls_fs) == 2
assert cls_fs[0].name == "a" and cls_fs[0].default is MISSING
assert cls_fs[1].name == "b" and cls_fs[1].default == 1

inst_fs = fields(F(a=5,b=6))
assert len(inst_fs) == 2
assert inst_fs[0].name == "a" and inst_fs[0].default is MISSING
assert inst_fs[1].name == "b" and inst_fs[1].default == 1

# 3) replace()
@dataclass
class R:
    a: int = field()
    b: int = field()

orig = R(a=1,b=2)
r2 = replace(orig, b=3)
assert r2 == R(a=1,b=3)

# unknown field
try:
    replace(orig, c=4)
    assert False
except TypeError:
    pass

# init=False
@dataclass
class R2:
    a: int = field()
    b: int = field(init=False)

r2obj = R2(a=1)
try:
    replace(r2obj, b=5)
    assert False
except ValueError:
    pass

# 4) asdict nondataclass
try:
    asdict(123)
    assert False
except TypeError:
    pass

# 5) asdict flat
@dataclass
class A1:
    a: int = field()
    b: int = 2

d1 = asdict(A1(a=9))
assert d1 == {"a":9,"b":2}

# nested dataclass
@dataclass
class A2:
    value: int = field()
    child: object = None

nested = A2(value=1, child=A2(value=2))
d2 = asdict(nested)
assert d2 == {"value":1, "child":{"value":2,"child":None}}

# nested list
@dataclass
class A3:
    value: int = field()
    children: list = field(default_factory=list)

inst = A3(value=1, children=[A3(value=2), A3(value=3)])
d3 = asdict(inst)
assert d3 == {
    "value":1,
    "children":[{"value":2,"children":[]}, {"value":3,"children":[]}],
}

# nested tuple
@dataclass
class A4:
    value: int = field()
    children: tuple = None

inst4 = A4(value=1, children=(A4(value=2), A4(value=3)))
d4 = asdict(inst4)
assert d4 == {
    "value":1,
    "children":(
        {"value":2,"children":None},
        {"value":3,"children":None},
    )
}

# nested dict
@dataclass
class A5:
    value: int = field()
    children: dict = field(default_factory=dict)

inst5 = A5(value=1, children={"x":A5(value=2), "y":A5(value=3)})
d5 = asdict(inst5)
assert d5 == {
    "value":1,
    "children":{
        "x":{"value":2,"children":{}},
        "y":{"value":3,"children":{}},
    }
}

# custom dict factory
@dataclass
class A6:
    value: int = field()
    child: object = None

def df_factory(pairs):
    return sorted(pairs, key=lambda kv: kv[0])

d6 = asdict(A6(value=1, child=A6(value=2)), dict_factory=df_factory)
assert d6 == [
    ("child",[("child",None),("value",2)]),
    ("value",1),
]

# 6) astuple
try:
    astuple(A1(a=1))
    assert False
except NotImplementedError:
    pass

# 7) make_dataclass
C1 = make_dataclass("C1",
    [("a",int, field(default=1)),
     ("b",int),
     "c"],
)
assert is_dataclass(C1)
fs1 = fields(C1)
assert len(fs1)==3
assert fs1[0].name=="a" and fs1[0].default==1
assert fs1[1].name=="b" and fs1[1].default is MISSING
assert fs1[2].name=="c" and fs1[2].default is MISSING

# namespace methods
C2 = make_dataclass("C2", ["value"], namespace={"square": lambda self: self.value**2})
c2 = C2(value=3)
assert c2.square() == 9

print("All extra tests passed.")
