CONVERT=convert 
SOURCES=sync.svg threaded.svg async.svg block.svg \
        reactor-1.svg
IMAGES=$(SOURCES:.svg=.png)

all: $(SOURCES) $(IMAGES)

%.png : %.svg
	$(CONVERT) $< $@

clean:
	rm *.png
