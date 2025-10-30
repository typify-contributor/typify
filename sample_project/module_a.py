from utils import greet
import module_b

class AClass:
    def __init__(self, name):
        self.name = name

    def show(self):
        print(f"AClass: My name is {self.name}")
        greet(self.name)

def func_a(x):
    print(f"func_a: received {x}")
    y = module_b.func_b(x + 1)
    print(f"func_a: func_b returned {y}")
    return y * 2
