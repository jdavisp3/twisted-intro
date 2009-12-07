CONVERT=convert 
SOURCES=sync.svg threaded.svg async.svg block.svg \
        reactor.svg reactor-callback.svg reactor-doread.svg \
        protocols-1.svg protocols-2.svg reactor-data-received.svg \
        reactor-poem-callback.svg deferred-1.svg deferred-2.svg \
        deferred-3.svg deferred-4.svg deferred-5.svg deferred-6.svg \
        reactor-deferred-callback.svg sync-async.svg
IMAGES=$(SOURCES:.svg=.png)

all: $(SOURCES) $(IMAGES)

%.png : %.svg
	$(CONVERT) $< $@

clean:
	rm *.png
