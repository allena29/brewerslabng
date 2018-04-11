BUNDLE_MAKEFILES = $(wildcard bundle/*/Makefile)
BUNDLES = $(dir $(BUNDLE_MAKEFILES))

.PHONY: $(BUNDLES)


all:
	$(MAKE) -C confvillain || exit 1
	for b in $(BUNDLES); do \
		$(MAKE) -C $$b || exit 1; \
	done

install-pyenv:
	./pyenv_installer
 
tempfs:
	[[ `uname` = 'Darwin' ]] && RD=`hdiutil attach -nomount ram://99000`;newfs_hfs -v 'pch-datastore' $$RD;mount -o noatime -t hfs $$RD datastore/tmpfs || echo 'Not running Darwin'
	[[ `uname` = 'Linux' ]] && sudo mount -t tmpfs -o size=50M tmpfs datastore/tmpfs || echo 'Not running Linux'
	mkdir datastore/tmpfs/running
	mkdir datastore/tmpfs/operational
	touch datastore/tmpfs/running/.gitkeep
	touch datastore/tmpfs/operational/.gitkeep
