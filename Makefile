
PACKAGE = airtools
VERSION = $(shell cat VERSION)

# installation prefix
prefix	= /usr/local

# files/directories
BINDIR  = $(DESTDIR)/$(prefix)/bin
DATADIR = $(DESTDIR)/$(prefix)/share/$(PACKAGE)
DOCDIR  = $(DESTDIR)/$(prefix)/share/doc/$(PACKAGE)
APPDIR  = $(DESTDIR)/$(prefix)/share/applications
PIXMAPSDIR = $(DESTDIR)/$(prefix)/share/pixmaps
DATA	= data/*
DOCS	= README* doc/manual-en.html
IMAGESDIR	= $(DOCDIR)/images
IMAGES	= doc/images/*

BIN 	= bayer2rgb pnmtomef pnmccdred pnmrowsort
BINSH 	= airtools airtools-cli airfun.sh aircmd.sh
BINPY	= airfun.py
JAR	= airtools-gui.jar
ANALYSIS = airds9.ana
DESKTOP	= airtools.desktop
ICON	= airtools.png
ICONSVG = airtools.svg

# compiler/linker definitions
CC = gcc
CFLAGS = -O4 -Wall
CFLAGS += -I/usr/include/netpbm
#LIBDCRAW = -lm -ljasper -ljpeg
LIBDCRAW = -lm -ljpeg
LIBPNM = -lm -lnetpbm

# special macro to be used in pnmccdred.c
LIBNETPBMPKG=$(shell dpkg-query -W -f '$${db:Status-Status} $${binary:Package}\n' libnetpbm*dev | grep "^installed" | cut -d ' ' -f2)
$(info package is $(LIBNETPBMPKG))
ifeq ($(LIBNETPBMPKG), libnetpbm10-dev)
  $(info using LIBNETPBM10)
  CFLAGS += -DLIBNETPBM10
else
  $(info LIBNETPBM10 is not set)
endif

# rules/targets
.c.o:
	$(CC) $(CFLAGS) -c $<

all:	$(BIN)

bayer2rgb: bayer2rgb.c bayer.o
	$(CC) $(CFLAGS) -o $@ bayer.o bayer2rgb.c -lm

pnmtomef: pnmtomef.c
	$(CC) $(CFLAGS) -o $@ pnmtomef.c $(LIBPNM)

pnmccdred: pnmccdred.c
	$(CC) $(CFLAGS) -o $@ pnmccdred.c $(LIBPNM)

pnmrowsort: pnmrowsort.c
	$(CC) $(CFLAGS) -o $@ pnmrowsort.c $(LIBPNM)

icon: $(ICONSVG)
	inkscape -o $(ICON) -C -w 64 -h 64 $(ICONSVG)

clean:
	-rm -f *.o
	rm -f $(BIN)
	#rm -f $(ICON)

install: all
	install -m 0755 -p $(BIN) $(BINSH) $(BINPY) $(BINDIR)
	install -m 0755 -d $(DATADIR)
	install -m 0644 -p $(DATA) $(DATADIR)
	install -m 0644 -p $(ANALYSIS) $(DATADIR)
	install -m 0644 -p $(JAR) $(DATADIR)
	install -m 0755 -d $(APPDIR)
	install -m 0644 -p $(DESKTOP) $(APPDIR)
	install -m 0755 -d $(DOCDIR)
	install -m 0644 -p $(DOCS) $(DOCDIR)
	install -m 0755 -d $(IMAGESDIR)
	install -m 0644 -p $(IMAGES) $(IMAGESDIR)
	install -m 0755 -d $(PIXMAPSDIR)
	install -m 0644 -p $(ICONSVG) $(PIXMAPSDIR)
	install -m 0644 -p $(ICON) $(DATADIR)

tarball:
	make clean
	test ! -d build && mkdir build || true
	(cd build; \
	rm -rf $(PACKAGE)-$(VERSION) && ln -s .. $(PACKAGE)-$(VERSION); \
	tar czf $(PACKAGE)_$(VERSION).orig.tar.gz -h \
		--exclude="*/.git*" --exclude="old" --exclude="doc/unused" --exclude="build" \
		--exclude="releases" --exclude="debian" $(PACKAGE)-$(VERSION); \
	rm -rf $(PACKAGE)-$(VERSION))

source:
	test ! -e build/$(PACKAGE)_$(VERSION).orig.tar.gz && make tarball || true
	(cd build; \
	tar xf $(PACKAGE)_$(VERSION).orig.tar.gz; \
	cd $(PACKAGE)-$(VERSION); \
	rsync -au ../../debian ./; \
	debuild -d -i -us -uc -S; \
	rm ../$(PACKAGE)_$(VERSION)*_source.*; \
	rm debian/files)
	rm -rf build/$(PACKAGE)-$(VERSION)
	ls -l build

debuild:
	(cd build && rm -rf $(PACKAGE)-$(VERSION) || true)
	$(eval DSCFILE := $(shell cd build && ls -t $(PACKAGE)_$(VERSION)-*.dsc | head -1))
	(cd build && dpkg-source -x $(DSCFILE))
	(cd build/$(PACKAGE)-$(VERSION) && debuild)
