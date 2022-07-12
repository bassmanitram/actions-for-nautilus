SHELL=/bin/bash
nautilus_path=`which nautilus`
install:
	mkdir -p ~/.local/share/nautilus-python/extensions/actions-for-nautilus
	mkdir -p ~/.local/share/actions-for-nautilus-configurator
	cp -a extensions ~/.local/share/nautilus-python
	cp -a configurator/* ~/.local/share/nautilus-python/
	cp -a ~/.local/share/nautilus-python/actions-for-nautilus-configurator.desktop ~/.local/share/applications
	@echo 'Restarting nautilus'
	@${nautilus_path} -q||true # This is due to nautilus -q always returning 255 status which causes makefile to think it failed

uninstall:
	rm -rf ~/.local/share/nautilus-python/extensions/actions-for-nautilus
	rm -f ~/.local/share/nautilus-python/extensions/actions-for-nautilus.py
	rm -rf ~/.local/share/actions-for-nautilus-configurator
	rm -f ~/.local/share/application/actions-for-nautilus-configurator.desktop
	@echo 'Restarting nautilus'
	@${nautilus_path} -q||true # This is due to nautilus -q always returning 255 status which causes makefile to think it failed
