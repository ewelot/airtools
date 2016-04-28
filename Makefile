
# installation prefix
prefix = /usr/local

# files/directories
PACKAGE = airtools
BINDIR = $(prefix)/bin
DATADIR = $(prefix)/share/$(PACKAGE)
EXTDIR = extern
PKGDIR = ..
DATA = data/*
DOCS = README GettingStarted.txt

BIN = dcraw-tl pnmtomef pnmccdred pnmcombine
BINSH = airfun.sh aircmd.sh
ANALYSIS = airds9.ana

# compiler/linker definitions
CC = gcc
CFLAGS = -O4 -Wall
LIBDCRAW = -lm -ljasper -ljpeg
LIBPNM = -lm -lnetpbm
ARCH := $(shell uname -m)


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

distclean: clean
	rm -rf $(EXTDIR)/*

install: all
	install -m 0755 -p $(BIN) $(BINSH) $(BINDIR)
	install -m 0644 -p $(ANALYSIS) $(BINDIR)
	install -m 0755 -d $(DATADIR)
	install -m 0644 -p $(DATA) $(DOCS) $(DATADIR)


##################################
# extern C programs
##################################

BINCDSCLIENT = aclient aclient_cgi vizquery findcat catcat findppmx findtyc2 find_gen
BINCEXAMPLES = imcopy fitscopy listhead
LIBFITS = -lcfitsio

externc: extract_externc cdsclient cexamples

extract_externc:
	test -d $(EXTDIR) || mkdir $(EXTDIR)
	for prog in cdsclient cexamples; do \
		test ! -s $(PKGDIR)/$$prog*tar* && \
			echo "WARNING: missing source archive for $$prog" && continue; \
		test -d $(EXTDIR)/$$prog* && continue; \
		echo "extracting $$prog"; \
		tar -C $(EXTDIR) -xf $(PKGDIR)/$$prog*tar*; \
	done

cdsclient:
	(cd $(EXTDIR)/cdsclient*; \
	test -s Makefile || ./configure --prefix=$(prefix); make)

cexamples:
	(cd $(EXTDIR)/cexamples; \
	test -s imcopy   || $(CC) $(CFLAGS) -o imcopy   imcopy.c   $(LIBFITS); \
	test -s fitscopy || $(CC) $(CFLAGS) -o fitscopy fitscopy.c $(LIBFITS); \
	test -s listhead || $(CC) $(CFLAGS) -o listhead listhead.c $(LIBFITS))

clean_externc:
	(cd $(EXTDIR)/cdsclient*; make clean)
	(cd $(EXTDIR)/cexamples; rm -f imcopy fitscopy listhead)

install_externc: externc
	(cd $(EXTDIR)/cdsclient*; install -m 0755 -p $(BINCDSCLIENT) $(BINDIR))
	(cd $(EXTDIR)/cexamples;  install -m 0755 -p $(BINCEXAMPLES) $(BINDIR))


##################################
# software from astromatic.net
##################################

BINASTROMATIC = sextractor scamp skymaker stiff swarp
ATLASLIBDIR = /usr/lib/atlas-base/atlas
ATLASINCDIR = /usr/include/atlas

astromatic: extract_astromatic $(BINASTROMATIC)

extract_astromatic:
	test -d $(EXTDIR) || mkdir $(EXTDIR)
	for prog in $(BINASTROMATIC); do \
		test ! -s $(PKGDIR)/$$prog*tar* && \
			echo "WARNING: missing source archive for $$prog" && continue; \
		test -d $(EXTDIR)/$$prog* && continue; \
		echo "extracting $$prog"; \
		tar -C $(EXTDIR) -xf $(PKGDIR)/$$prog*tar*; \
	done

sextractor scamp:
	test ! -d $(EXTDIR)/$@* || \
	(cd $(EXTDIR)/$@*; \
	test -s Makefile || \
	./configure --prefix=$(prefix) \
		--with-atlas-incdir=$(ATLASINCDIR) \
		--with-atlas-libdir=$(ATLASLIBDIR); \
	make)

skymaker stiff swarp:
	(cd $(EXTDIR)/$@*; \
	test -s Makefile || ./configure --prefix=$(prefix); make)

install_astromatic: astromatic
	for prog in $(BINASTROMATIC); do \
		test ! -d $(EXTDIR)/$$prog* || \
		(cd $(EXTDIR)/$$prog*; make install); \
	done


##################################
# precompiled SAOImage DS9
##################################

BINDS9 = ds9
DS9TAR := $(wildcard $(PKGDIR)/ds9.linux.*tar*)
ifeq ($(ARCH), x86_64)
	DS9TAR := $(wildcard $(PKGDIR)/ds9.linux64.*tar*)
endif

install_ds9:
	$(info installing $(BINDS9))
	test -d $(EXTDIR) || mkdir $(EXTDIR)
	tar -C $(EXTDIR) -xf $(DS9TAR) && \
	install -m 0755 -p $(EXTDIR)/$(BINDS9) $(BINDIR)

	
##################################
# java program stilts
##################################

BINSTILTS = stilts stilts.jar

install_stilts:
	$(info Installing stilts)
	for prog in $(BINSTILTS); do \
		test ! -s $(PKGDIR)/$$prog && \
			echo "WARNING: missing file $$prog" && continue; \
		install -m 0755 -p $(PKGDIR)/$$prog $(BINDIR); \
	done
