echo "Unistall RNAival? [y/n]"
select selectReply in "yes" "no"; do
	filteredReply=${selectReply:-$REPLY}
	case $filteredReply in 
		Yes | yes | y ) echo "Removing dependencies and desktop entries."
			rm -r "$( realpath ~)/RNAival_Dependencies"
			if [ -f "/usr/share/applications/RNAival.desktop" ] ; then
				echo "Removing desktop file (requires pasword)."
				sudo rm /usr/share/applications/RNAival.desktop
			fi
			if [ -f "$( realpath ~)/.local/share/applications/RNAival.desktop" ]; then
				rm "$( realpath ~)/.local/share/applications/RNAival.desktop"
			fi
			echo "Uninstallation sucessfull."
			break;;
		No | no | n ) echo "Uninstallation cancelled."
			break;;
	esac
done
