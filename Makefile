SHELL=/bin/bash
nautilus_path=`which nautilus`
GLOBALLOC=/usr/share
LOCALLOC=~/.local/share

install:
	mkdir -p $(LOCALLOC)/nautilus-python/extensions/actions-for-nautilus
	mkdir -p $(LOCALLOC)/actions-for-nautilus-configurator
	mkdir -p $(LOCALLOC)/applications
	cp -a extensions $(LOCALLOC)/nautilus-python
	cp -a configurator/* $(LOCALLOC)/actions-for-nautilus-configurator
	LOC=$(LOCALLOC) python -c 'import os,sys; sys.stdout.write(os.path.expandvars(sys.stdin.read()))' \
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
	mkdir -p $(GLOBALLOC)/nautilus-python
	mkdir -p $(GLOBALLOC)/actions-for-nautilus-configurator
	mkdir -p $(GLOBALLOC)/applications
	cp -a extensions $(GLOBALLOC)/nautilus-python
	cp -a configurator/* $(GLOBALLOC)/actions-for-nautilus-configurator
	LOC=$(GLOBALLOC) python -c 'import os,sys; sys.stdout.write(os.path.expandvars(sys.stdin.read()))' \
		< $(GLOBALLOC)/actions-for-nautilus-configurator/actions-for-nautilus-configurator.desktop \
		> $(GLOBALLOC)/applications/actions-for-nautilus-configurator.desktop
	@echo 'You must now restart nautilus by running the command "nautilus -q"'
	@echo 'You may also have to restart the gnome shell in order to see the configuration application'

uninstall_global:
	rm -rf $(GLOBALLOC)/nautilus-python/extensions/actions-for-nautilus
	rm -f $(GLOBALLOC)/nautilus-python/extensions/actions-for-nautilus.py
	rm -rf $(GLOBALLOC)/actions-for-nautilus-configurator
	rm -f $(GLOBALLOC)/applications/actions-for-nautilus-configurator.desktop
	@echo 'You must now restart nautilus by running the command "nautilus -q"'
	@echo 'You may also have to restart the gnome shell in order to no longer see the configuration application'
