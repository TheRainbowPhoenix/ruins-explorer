def add_a(a: float, b: float) -> float:
    return a + b

a = 2.0
b = 3.0
c = add_a(a, b)
print(c)


class TestThing:
    def __init__(self):
        self._hp = 0
    
    @property
    def hp(self): return self._hp

    @hp.setter
    def hp(self, value): 
        self._hp = value

t = TestThing()
print(t.hp)
t.hp = 42
print(t.hp)