def task1(x: list[float], n: int = 20, repl: int = 200) -> list[float]:
    return [el if el is not n else repl for el in x]

def task2(x: list[str]) -> list[str]:
    return [el for el in x if el != ""]

def task3(x: list[float]) -> list[float]:
    return [el * el for el in x]

def task4(x: list[float], n: int = 20) -> list[float]:
    return [el for el in x if el != n] 


print(task1([1, 2, 3, 20, 50, 20, 123, 20]))
print(task2(["", "asdsda", "asddas", "", ""]))
print(task3([1, 2, 3, 4, 5]))
print(task4([1, 2, 3, 20, 50, 20, 123, 20]))