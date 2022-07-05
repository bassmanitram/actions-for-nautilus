SHELL=/bin/bash
nautilus_path=`which nautilus`
install:
	mkdir -p ~/.local/share/nautilus-python/extensions/actions-for-nautilus
	cp actions-for-nautilus.py ~/.local/share/nautilus-python/extensions
	cp actions_for_nautilus.py config.json ~/.local/share/nautilus-python/extensions/actions-for-nautilus
	@echo 'Restarting nautilus'
	@${nautilus_path} -q||true # This is due to nautilus -q always returning 255 status which causes makefile to think it failed

uninstall:
	rm ~/.local/share/nautilus-python/extensions/actions-for-nautilus.py
	rm -rf ~/.local/share/nautilus-python/extensions/actions-for-nautilus
	@echo 'Restarting nautilus'
	@${nautilus_path} -q||true # This is due to nautilus -q always returning 255 status which causes makefile to think it failed
