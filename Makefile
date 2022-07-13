SHELL=/bin/bash
nautilus_path=`which nautilus`
install:
	mkdir -p ~/.local/share/nautilus-python/extensions/actions-for-nautilus
	mkdir -p ~/.local/share/actions-for-nautilus-configurator
	cp -a extensions ~/.local/share/nautilus-python
	[ -f ~/.local/share/nautilus-python/extensions/actions-for-nautilus/config.json ] || \
		cp ~/.local/share/nautilus-python/extensions/actions-for-nautilus/sqmple-config.json ~/.local/share/nautilus-python/extensions/actions-for-nautilus/config.json
	cp -a configurator/* ~/.local/share/actions-for-nautilus-configurator
	python -c 'import os,sys; sys.stdout.write(os.path.expandvars(sys.stdin.read()))' \
		< ~/.local/share/actions-for-nautilus-configurator/actions-for-nautilus-configurator.desktop \
		> ~/.local/share/applications/actions-for-nautilus-configurator.desktop
	@echo 'Restarting nautilus'
	@${nautilus_path} -q||true # This is due to nautilus -q always returning 255 status which causes makefile to think it failed

uninstall:
	rm -rf ~/.local/share/nautilus-python/extensions/actions-for-nautilus
	rm -f ~/.local/share/nautilus-python/extensions/actions-for-nautilus.py
	rm -rf ~/.local/share/actions-for-nautilus-configurator
	rm -f ~/.local/share/application/actions-for-nautilus-configurator.desktop
	@echo 'Restarting nautilus'
	@${nautilus_path} -q||true # This is due to nautilus -q always returning 255 status which causes makefile to think it failed
