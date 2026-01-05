VERSION=2.0.0

# Installation location when 'make install' or 'make uninstall' is used
LOCALLOC=~/.local/share

# Installation location when 'make install-global' or 'make uninstall-global' is used
GLOBALLOC=/usr/local/share

# For a successful package build, the executing user must be 'root'
nautilus_path = $(shell which nautilus)

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
	@echo 'in your application launcher'

uninstall:
	rm -rf $(LOCALLOC)/nautilus-python/extensions/actions-for-nautilus
	rm -rf $(LOCALLOC)/actions-for-nautilus-configurator
	rm -f $(LOCALLOC)/applications/actions-for-nautilus-configurator.desktop
	@echo 'Restarting nautilus'
	@${nautilus_path} -q||true # This is due to nautilus -q always returning 255 status which causes makefile to think it failed
	@echo 'You may have to restart the gnome shell in order to no longer see the configuration application'
	@echo 'in your application launcher'

clean:
	rm -rf build dist

install-global:
	mkdir -p $(GLOBALLOC)/nautilus-python/extensions/actions-for-nautilus
	mkdir -p $(GLOBALLOC)/actions-for-nautilus-configurator
	mkdir -p $(GLOBALLOC)/applications
	cp -a extensions $(GLOBALLOC)/nautilus-python
	cp -a configurator/* $(GLOBALLOC)/actions-for-nautilus-configurator
	LOC=$(GLOBALLOC) python3 -c 'import os,sys; sys.stdout.write(os.path.expandvars(sys.stdin.read()))' \
		< $(GLOBALLOC)/actions-for-nautilus-configurator/actions-for-nautilus-configurator.desktop \
		> $(GLOBALLOC)/applications/actions-for-nautilus-configurator.desktop
	@echo 'Restarting nautilus'
	@${nautilus_path} -q||true # This is due to nautilus -q always returning 255 status which causes makefile to think it failed
	@echo 'You may also have to restart the gnome shell in order to see the configuration application'
	@echo 'in your application launcher'

# You must be root to do this
uninstall-global:
	rm -rf $(GLOBALLOC)/nautilus-python/extensions/actions-for-nautilus
	rm -rf $(GLOBALLOC)/actions-for-nautilus-configurator
	rm -f $(GLOBALLOC)/applications/actions-for-nautilus-configurator.desktop
	@echo 'Restarting nautilus'
	@${nautilus_path} -q||true # This is due to nautilus -q always returning 255 status which causes makefile to think it failed
	@echo 'You may also have to restart the gnome shell in order to no longer see the configuration application'
	@echo 'in your application launcher'

# You must be root to do this
deb:
	mkdir -p build/$(GLOBALLOC)/nautilus-python/extensions/actions-for-nautilus
	mkdir -p build/$(GLOBALLOC)/actions-for-nautilus-configurator
	mkdir -p build/$(GLOBALLOC)/applications
	cp -a extensions build/$(GLOBALLOC)/nautilus-python
	cp -a configurator/* build/$(GLOBALLOC)/actions-for-nautilus-configurator
	LOC=$(GLOBALLOC) python3 -c 'import os,sys; sys.stdout.write(os.path.expandvars(sys.stdin.read()))' \
		< build/$(GLOBALLOC)/actions-for-nautilus-configurator/actions-for-nautilus-configurator.desktop \
		> build/$(GLOBALLOC)/applications/actions-for-nautilus-configurator.desktop
	rm build/$(GLOBALLOC)/actions-for-nautilus-configurator/actions-for-nautilus-configurator.desktop
	mkdir -p build/DEBIAN
	mkdir -p build/usr/share/doc/actions-for-nautilus
	VERSION=$(VERSION) python3 -c 'import os,sys; sys.stdout.write(os.path.expandvars(sys.stdin.read()))' \
		< packaging/DEBIAN/control \
		> build/DEBIAN/control
	cp packaging/doc/actions-for-nautilus/* build/usr/share/doc/actions-for-nautilus
	mkdir -p dist
	dpkg-deb --build --root-owner-group build dist/actions-for-nautilus_$(VERSION)_all.deb
