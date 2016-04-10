#!/bin/sh
# Enable and disable HDMI output on the Raspberry Pi
# Thanks to https://gist.github.com/AGWA/9874925

# NOTE: Not currently using, because having trouble waking display

is_off ()
{
	tvservice -s | grep "TV is off" >/dev/null
}

case $1 in
	off)
		tvservice -o
	;;
	on)
		if is_off
		then
			tvservice -p
			sleep 2
			curr_vt=`fgconsole`
			if [ "$curr_vt" = "1" ]
			then
				chvt 2
				sleep 1
				chvt 1
			else
				chvt 1
				sleep 1
				chvt "$curr_vt"
			fi
		fi
	;;
	status)
		if is_off
		then
			echo off
		else
			echo on
		fi
	;;
	*)
		echo "Usage: $0 on|off|status" >&2
		exit 2
	;;
esac

exit 0