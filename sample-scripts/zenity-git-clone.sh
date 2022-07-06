env | sort >> /tmp/zgc.log
echo "1: $1" >> /tmp/zgc.log
if [ -d "$1" ]; then
	gitrepo=$(zenity --entry --text "Enter GIT repo URL" --title "git clone into $1" --width 800)
	echo "gitrepo $gitrepo" >> /tmp/zgc.log
	if [ "$gitrepo" ]; then  
		cd "$1" || { zenity --error --text "Could not change to folder $1"; exit 1; }
		git clone "$gitrepo" || { zenity --error --text "Could clone $$gitrepo into folder $1"; exit 1; }
	fi
else
	echo "$1 is not a folder"
fi
