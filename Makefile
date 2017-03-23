
PACKAGE = airtools
VERSION = 1.2

# installation prefix
prefix	= /usr/local

# files/directories
BINDIR  = $(DESTDIR)/$(prefix)/bin
DATADIR = $(DESTDIR)/$(prefix)/share/$(PACKAGE)
DOCDIR  = $(DESTDIR)/$(prefix)/share/doc/$(PACKAGE)
DATA	= data/*
DOCS	= README* doc/*

BIN 	= dcraw-tl pnmtomef pnmccdred pnmcombine
BINSH 	= airfun.sh aircmd.sh
ANALYSIS = airds9.ana

# compiler/linker definitions
CC = gcc
CFLAGS = -O4 -Wall
LIBDCRAW = -lm -ljasper -ljpeg
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

clean:
	-rm -f *.o
	rm -f $(BIN)

install: all
	install -m 0755 -p $(BIN) $(BINSH) $(BINDIR)
	install -m 0755 -d $(DATADIR)
	install -m 0644 -p $(DATA) $(DATADIR)
	install -m 0644 -p $(ANALYSIS) $(DATADIR)
	install -m 0755 -d $(DOCDIR)
	install -m 0644 -p $(DOCS) $(DOCDIR)

tarball:
	make clean
	(cd ..; tar czf $(PACKAGE)_$(VERSION).orig.tar.gz --exclude="*/.git" \
		$(PACKAGE)-$(VERSION))

