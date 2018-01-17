
PACKAGE = airtools
VERSION = 2.1

# installation prefix
prefix	= /usr/local

# files/directories
BINDIR  = $(DESTDIR)/$(prefix)/bin
DATADIR = $(DESTDIR)/$(prefix)/share/$(PACKAGE)
DOCDIR  = $(DESTDIR)/$(prefix)/share/doc/$(PACKAGE)
APPDIR  = $(DESTDIR)/$(prefix)/share/applications
DATA	= data/*
DOCS	= README* doc/README* doc/*txt doc/manual-de.html
IMAGESDIR	= $(DOCDIR)/images
IMAGES	= doc/images/*

BIN 	= dcraw-tl pnmtomef pnmccdred pnmcombine pnmrowsort
BINSH 	= airfun.sh aircmd.sh airtools_launcher.sh
ANALYSIS = airds9.ana
DESKTOP	= airtools.desktop

# compiler/linker definitions
CC = gcc
CFLAGS = -O4 -Wall
#LIBDCRAW = -lm -ljasper -ljpeg
LIBDCRAW = -lm -ljpeg
LIBPNM = -lm -lnetpbm


# rules/targets
.c.o:
	$(CC) $(CFLAGS) -c $<

all:	$(BIN)

dcraw-tl: dcraw-tl.c
	$(CC) $(CFLAGS) -o $@ dcraw-tl.c $(LIBDCRAW)

pnmtomef: pnmtomef.c
	$(CC) $(CFLAGS) -o $@ pnmtomef.c $(LIBPNM)

pnmccdred: pnmccdred.c
	$(CC) $(CFLAGS) -o $@ pnmccdred.c $(LIBPNM)

pnmcombine: pnmcombine.o functions.o
	$(CC) $(CFLAGS) -o $@ $^ $(LIBPNM)

pnmrowsort: pnmrowsort.c
	$(CC) $(CFLAGS) -o $@ pnmrowsort.c $(LIBPNM)

clean:
	-rm -f *.o
	rm -f $(BIN)

install: all
	install -m 0755 -p $(BIN) $(BINSH) $(BINDIR)
	install -m 0755 -d $(DATADIR)
	install -m 0644 -p $(DATA) $(DATADIR)
	install -m 0644 -p $(ANALYSIS) $(DATADIR)
	install -m 0755 -d $(APPDIR)
	install -m 0644 -p $(DESKTOP) $(APPDIR)
	install -m 0755 -d $(DOCDIR)
	install -m 0644 -p $(DOCS) $(DOCDIR)
	install -m 0755 -d $(IMAGESDIR)
	install -m 0644 -p $(IMAGES) $(IMAGESDIR)

tarball:
	make clean
	(cd ..; \
	test ! -e $(PACKAGE)-$(VERSION) && ln -s $(PACKAGE) $(PACKAGE)-$(VERSION); \
	tar czf $(PACKAGE)_$(VERSION).orig.tar.gz -h --exclude="*/.git" \
		$(PACKAGE)-$(VERSION))

