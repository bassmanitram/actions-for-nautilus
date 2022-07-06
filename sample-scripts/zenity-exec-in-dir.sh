env | sort >> /tmp/zgc.log
echo "1: $1" >> /tmp/zgc.log
if [ -d "$1" ]; then
	cmd=$(zenity --entry --text "Enter command" --title "execute command in $1" --width 800)
	echo "cmd $gitrepo" >> /tmp/zgc.log
	if [ "$cmd" ]; then  
		cd $(readlink -f "$1")
		$cmd
	fi
else
	echo "$1 is not a folder" >> /tmp/zgc.log
fi
