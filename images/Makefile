CONVERT=convert 
SOURCES=sync.svg threaded.svg async.svg block.svg \
        reactor.svg reactor-callback.svg
IMAGES=$(SOURCES:.svg=.png)

all: $(SOURCES) $(IMAGES)

%.png : %.svg
	$(CONVERT) $< $@

clean:
	rm *.png
