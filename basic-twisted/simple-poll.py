import platform
if platform.system() == 'Windows':
    print("Pollreactor not supported")
else:
    from twisted.internet import pollreactor
    pollreactor.install()

from twisted.internet import reactor
reactor.run()
