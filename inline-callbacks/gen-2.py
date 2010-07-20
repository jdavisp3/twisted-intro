
def my_generator():
    print 'starting up'
    yield 1
    print "workin'"
    yield 2
    print "still workin'"
    yield 3
    print 'done'

gen = my_generator()

while True:
    try:
        n = gen.next()
    except StopIteration:
        break
    else:
        print n
