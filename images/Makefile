CONVERT=convert 
SOURCES=sync.svg threaded.svg async.svg block.svg \
        reactor.svg reactor-callback.svg reactor-doread.svg
IMAGES=$(SOURCES:.svg=.png)

all: $(SOURCES) $(IMAGES)

%.png : %.svg
	$(CONVERT) $< $@

clean:
	rm *.png
