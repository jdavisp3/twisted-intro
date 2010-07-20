
class Malfunction(Exception):
    pass

def my_generator():
    print 'starting up'

    val = yield 1
    print 'got:', val

    val = yield 2
    print 'got:', val

    try:
        yield 3
    except Malfunction:
        print 'malfunction!'

    yield 4

    print 'done'

gen = my_generator()

print gen.next()
print gen.send(10)
print gen.send(20)
print gen.throw(Malfunction())
try:
    gen.next()
except StopIteration:
    pass
