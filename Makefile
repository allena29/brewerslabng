THING_MAKEFILES = $(wildcard things/*/Makefile)
THINGS = $(dir $(THING_MAKEFILES))

.PHONY: $(THINGS) yang things pyconfhoard

all: pyconfhoard yang things

pyconfhoard:
	$(MAKE) -C pyconfhoard || exit 1

yang:
	$(MAKE) -C yang || exit 1

things:
	for b in $(THINGS); do \
		$(MAKE) -C $$b || exit 1; \
	done

tempfs:
	[[ `uname` = 'Darwin' ]] && RD=`hdiutil attach -nomount ram://99000`;newfs_hfs -v 'pch-datastore' $$RD;mount -o noatime -t hfs $$RD datastore/tmpfs || echo 'Not running Darwin'
	[[ `uname` = 'Linux' ]] && sudo mount -t tmpfs -o size=50M tmpfs datastore/tmpfs || echo 'Not running Linux'
	mkdir datastore/tmpfs/running
	mkdir datastore/tmpfs/operational
	touch datastore/tmpfs/running/.gitkeep
	touch datastore/tmpfs/operational/.gitkeep
