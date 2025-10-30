import module_a 
from utils import farewell

class BClass:
    def __init__(self, value):
        self.value = value

    def compute(self):
        print(f"BClass: computing with {self.value}")
        result = module_a.func_a(self.value)
        print(f"BClass: result from func_a = {result}")
        farewell("BClass user")
        return result + 10

def func_b(y):
    print(f"func_b: received {y}")
    return y + 5
