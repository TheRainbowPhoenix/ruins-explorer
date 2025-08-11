# test_udataclasses.py   — plain-Python tests (no pytest)

from udataclasses import dataclass, field, FrozenInstanceError

# 1) empty
@dataclass
class Empty:
    pass

# should construct without error
Empty()

# 2) excluded fields
@dataclass
class Excl:
    a: int = field()
    b: int = field(default=0, init=False)

try:
    Excl(a=1, b=2)
    assert False, "Expected TypeError for b as init=False"
except TypeError:
    pass

# correct usage
e = Excl(a=1)
assert e.a == 1 and e.b == 0

# 3) keyword-only init
@dataclass
class KW:
    a: int = field()
    b: int = field()

try:
    # positional args should fail
    KW(1, 2)
    assert False, "Expected TypeError for positional args"
except TypeError:
    pass

kw = KW(a=1, b=2)
assert kw.a == 1 and kw.b == 2

# 4) post_init
collected = None
@dataclass
class Post:
    a: int = field()
    def __post_init__(self):
        global collected
        collected = self.a

Post(a=5)
assert collected == 5

# 5) repr with repr=False
@dataclass
class ReprTest:
    a: int = field()
    b: int = field()
    c: int = field(repr=False)

r = ReprTest(a=1, b=2, c=3)
assert repr(r) == "ReprTest(a=1, b=2)"

# 6) default and equality
@dataclass
class Default:
    a: int = field()
    b: int = 0

assert Default(a=1) == Default(a=1, b=0)
assert Default(a=1, b=9) == Default(a=1, b=9)

# 7) default_factory
@dataclass
class DefFact:
    a: list = field(default_factory=lambda: [])

x1 = DefFact()
x1.a.append(42)
assert x1.a == [42]
x2 = DefFact()
assert x2.a == []

# 8) mutable property on non-frozen
@dataclass
class Prop:
    a: int = field()

p = Prop(a=7)
assert p.a == 7
p.a = 8
assert p.a == 8

# 9) eq vs compare=False
@dataclass
class EqTest:
    a: int = field()
    b: int = field()
    c: int = field(compare=False)

assert EqTest(a=1,b=2,c=9) == EqTest(a=1,b=2,c=0)
assert not (EqTest(a=1,b=2,c=3) == EqTest(a=1,b=3,c=3))

# 10) ordering
@dataclass(order=True)
class OrdTest:
    a: int = field()
    b: int = field()
    c: int = field(compare=False)

assert OrdTest(a=1,b=2,c=9) <= OrdTest(a=1,b=2,c=0)
assert not (OrdTest(a=1,b=2,c=9) <  OrdTest(a=1,b=2,c=0))

# 11) frozen
@dataclass(frozen=True)
class Frozen:
    a: int = field()

f = Frozen(a=1)
try:
    f.a = 2
    assert False, "Should not allow assignment on frozen"
except FrozenInstanceError:
    pass
try:
    del f.a
    assert False, "Should not allow deletion on frozen"
except FrozenInstanceError:
    pass

# 12) implicit hash
@dataclass(eq=True, frozen=True)
class ImpHash:
    a: int = field()
    b: int = field()

assert hash(ImpHash(a=1,b=2)) == hash(ImpHash(a=1,b=2))
assert ImpHash.__hash__ is not None

# 13) disabled hash
@dataclass(eq=True, frozen=False)
class DisHash:
    a: int = field()
    def __hash__(self):
        return 4

assert DisHash.__hash__ is None

# 14) inherited custom hash
@dataclass(eq=False)
class InhHash:
    a: int = field()
    b: int = field()
    def __hash__(self):
        return 99

assert hash(InhHash(a=1,b=2)) == 99

# 15) unsafe_hash
@dataclass(unsafe_hash=True)
class Unsafe:
    a: int = field()
    b: int = field()

assert Unsafe.__hash__ is not None
assert hash(Unsafe(a=1,b=2)) == hash(Unsafe(a=1,b=2))

# 16) inherited fields
@dataclass
class Base:
    a: int = field()

@dataclass
class Sub(Base):
    b: int = field()

s = Sub(a=3,b=4)
assert (s.a, s.b) == (3,4)

# 17) override inherited field
@dataclass
class Base2:
    x: int = 1

@dataclass
class Sub2(Base2):
    x: int = 2

assert Base2().x == 1
assert Sub2().x == 2

print("All tests passed.")
