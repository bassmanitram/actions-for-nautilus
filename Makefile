SHELL=/bin/bash
nautilus_path=`which nautilus`
GLOBALLOC=/usr/share
LOCALLOC=~/.local/share
VERSION="1.4.0"

install:
	mkdir -p $(LOCALLOC)/nautilus-python/extensions/actions-for-nautilus
	mkdir -p $(LOCALLOC)/actions-for-nautilus-configurator
	mkdir -p $(LOCALLOC)/applications
	cp -a extensions $(LOCALLOC)/nautilus-python
	cp -a configurator/* $(LOCALLOC)/actions-for-nautilus-configurator
	LOC=$(LOCALLOC) python3 -c 'import os,sys; sys.stdout.write(os.path.expandvars(sys.stdin.read()))' \
		< $(LOCALLOC)/actions-for-nautilus-configurator/actions-for-nautilus-configurator.desktop \
		> $(LOCALLOC)/applications/actions-for-nautilus-configurator.desktop
	@echo 'Restarting nautilus'
	@${nautilus_path} -q||true # This is due to nautilus -q always returning 255 status which causes makefile to think it failed
	@echo 'You may have to restart the gnome shell in order to see the configuration application'

uninstall:
	rm -rf $(LOCALLOC)/nautilus-python/extensions/actions-for-nautilus
	rm -f $(LOCALLOC)/nautilus-python/extensions/actions-for-nautilus.py
	rm -rf $(LOCALLOC)/actions-for-nautilus-configurator
	rm -f $(LOCALLOC)/applications/actions-for-nautilus-configurator.desktop
	@echo 'Restarting nautilus'
	@${nautilus_path} -q||true # This is due to nautilus -q always returning 255 status which causes makefile to think it failed
	@echo 'You may have to restart the gnome shell in order to no longer see the configuration application'

install_global:
ifneq ($(shell id -u), 0)
	@echo "You must be root to perform this action."
	exit 1
else
	mkdir -p $(GLOBALLOC)/nautilus-python
	mkdir -p $(GLOBALLOC)/actions-for-nautilus-configurator
	mkdir -p $(GLOBALLOC)/applications
	cp -a extensions $(GLOBALLOC)/nautilus-python
	cp -a configurator/* $(GLOBALLOC)/actions-for-nautilus-configurator
	LOC=$(GLOBALLOC) python3 -c 'import os,sys; sys.stdout.write(os.path.expandvars(sys.stdin.read()))' \
		< $(GLOBALLOC)/actions-for-nautilus-configurator/actions-for-nautilus-configurator.desktop \
		> $(GLOBALLOC)/applications/actions-for-nautilus-configurator.desktop
	@echo 'You must now restart nautilus by running the command "nautilus -q"'
	@echo 'You may also have to restart the gnome shell in order to see the configuration application'
endif

uninstall_global:
ifneq ($(shell id -u), 0)
	@echo "You must be root to perform this action."
	exit 1
else
	rm -rf $(GLOBALLOC)/nautilus-python/extensions/actions-for-nautilus
	rm -f $(GLOBALLOC)/nautilus-python/extensions/actions-for-nautilus.py
	rm -rf $(GLOBALLOC)/actions-for-nautilus-configurator
	rm -f $(GLOBALLOC)/applications/actions-for-nautilus-configurator.desktop
	@echo 'You must now restart nautilus by running the command "nautilus -q"'
	@echo 'You may also have to restart the gnome shell in order to no longer see the configuration application'
endif

deb:
ifneq ($(shell id -u), 0)
	@echo "You must be root to perform this action."
	exit 1
else
	rm -rf build
	mkdir -p build/$(GLOBALLOC)/nautilus-python
	mkdir -p build/$(GLOBALLOC)/actions-for-nautilus-configurator
	mkdir -p build/$(GLOBALLOC)/applications
	mkdir -p build/$(GLOBALLOC)/doc/actions-for-nautilus
	mkdir -p build/DEBIAN
	cp -r --preserve=mode,timestamps extensions build/$(GLOBALLOC)/nautilus-python
	cp -r --preserve=mode,timestamps configurator/* build/$(GLOBALLOC)/actions-for-nautilus-configurator
	rm build/$(GLOBALLOC)/actions-for-nautilus-configurator/javascript/jquery.min.js
	LOC=$(GLOBALLOC) python3 -c 'import os,sys; sys.stdout.write(os.path.expandvars(sys.stdin.read()))' \
		< build/$(GLOBALLOC)/actions-for-nautilus-configurator/actions-for-nautilus-configurator.desktop \
		> build/$(GLOBALLOC)/applications/actions-for-nautilus-configurator.desktop
	VERSION=$(VERSION) python3 -c 'import os,sys; sys.stdout.write(os.path.expandvars(sys.stdin.read()))' \
		< packaging/DEBIAN/control \
		> build/DEBIAN/control
	cp -r --preserve=mode,timestamps packaging/doc build/$(GLOBALLOC)
	cp README.md build/$(GLOBALLOC)/doc/actions-for-nautilus
	cp RELEASE-NOTES.md build/$(GLOBALLOC)/doc/actions-for-nautilus/NEWS
	mv build/$(GLOBALLOC)/actions-for-nautilus-configurator/README.md build/$(GLOBALLOC)/doc/actions-for-nautilus/configurator.README.md
	gzip -n9 build/$(GLOBALLOC)/doc/actions-for-nautilus/NEWS
	gzip -n9 build/$(GLOBALLOC)/doc/actions-for-nautilus/changelog
	find build/ -type d -exec chmod 0755 {} \;
	find build/ -type f -exec chmod 0644 {} \;
	chmod +x build/$(GLOBALLOC)/actions-for-nautilus-configurator/start-configurator.sh
endif
	dpkg-deb --build build dist/actions-for-nautilus_$(VERSION)_all.deb
	lintian dist/actions-for-nautilus_$(VERSION)_all.deb
