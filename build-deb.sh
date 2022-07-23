tmp_dir=$(mktemp -d -t a4n-XXXXXXXXXX)
mkdir -p $tmp_dir/usr/share/actions-for-nautilus
mkdir -p $tmp_dir/usr/share/nautilus-python

cp -r --preserve=mode extensions   $tmp_dir/usr/share/nautilus-python
cp -r --preserve=mode configurator $tmp_dir/usr/share/actions-for-nautilus

python -c 'import os,sys; sys.stdout.write(os.path.expandvars(sys.stdin.read()))' \
	< ~/.local/share/actions-for-nautilus-configurator/actions-for-nautilus-configurator.desktop \
	> ~/.local/share/applications/actions-for-nautilus-configurator.desktop
