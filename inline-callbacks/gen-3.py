
def my_generator():
    yield 1
    yield 2
    yield 3

def my_other_generator():
    yield 10
    yield 20
    yield 30
    yield 40

gens = [my_generator(), my_other_generator()]

while gens:
    for g in gens[:]:
        try:
            n = g.next()
        except StopIteration:
            gens.remove(g)
        else:
            print n
