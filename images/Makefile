CONVERT=convert 
SOURCES=sync.svg threaded.svg async.svg block.svg \
        reactor.svg reactor-callback.svg reactor-doread.svg \
        protocols-1.svg protocols-2.svg reactor-data-received.svg \
        reactor-poem-callback.svg deferred-1.svg \
        reactor-deferred-callback.svg
IMAGES=$(SOURCES:.svg=.png)

all: $(SOURCES) $(IMAGES)

%.png : %.svg
	$(CONVERT) $< $@

clean:
	rm *.png
