#!/bin/sh

Delim=,
sorting=cat
random=cat
N=5

while getopts n:d:SR name; do
	case $name in
		n) N=$OPTARG ;;
		d) Delim=$OPTARG ;;
		S) sorting=sort ;;
		R) random=shuf ;;
	esac
done

shift $((OPTIND - 1))
col=${1:-1}
cut -d $Delim -f $col | $sorting | $random | head -${N}

