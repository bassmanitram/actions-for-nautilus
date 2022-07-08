SHELL=/bin/bash
nautilus_path=`which nautilus`
install:
	mkdir -p ~/.local/share/nautilus-python/extensions/actions-for-nautilus
	cp -r extensions ~/.local/share/nautilus-python
	@echo 'Restarting nautilus'
	@${nautilus_path} -q||true # This is due to nautilus -q always returning 255 status which causes makefile to think it failed

uninstall:
	rm ~/.local/share/nautilus-python/extensions/actions-for-nautilus.py
	rm -rf ~/.local/share/nautilus-python/extensions/actions-for-nautilus
	@echo 'Restarting nautilus'
	@${nautilus_path} -q||true # This is due to nautilus -q always returning 255 status which causes makefile to think it failed
