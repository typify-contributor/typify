from module_a import AClass, func_a
from module_b import BClass
from utils import greet, farewell

def main():
    greet("User")

    a = AClass("Alice")
    a.show()

    result_a = func_a(10)
    print(f"Result from func_a: {result_a}")

    b = BClass(20)
    result_b = b.compute()
    print(f"Result from BClass.compute(): {result_b}")

    farewell("User")

if __name__ == "__main__":
    main()
