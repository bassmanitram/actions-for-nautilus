MY_HOME=$(pwd $(dirname $0))
cd $HOME/.local/share/actions-for-nautilus
if [[ ! -f "my-config.json" ]]; then
	mv config.json my-config.json
fi
if [[ "$1" == "0" ]]; then
	ln -fs my-config.json config.json
else
	ln -fs $MY_HOME/configurator/sample-config.json config.json
fi
