#!/bin/sh
N=5
D=,
var=cat


usage(){
	echo usage: column.sh [ -n N -d D -S -R ] column
}

while getopts n:d:SRh option; do
	case $option in
		n) N=$OPTARG ;;
		d) D=$OPTARG ;;
		S) var=sort ;;
		R) var=shuf ;;
		h) usage ;;
		*) echo "Invalid Argument"
			exit 1 ;;

	esac
done
shift $((OPTIND - 1))
col=${1:-1}
cut -d $D -f $col | $var | head -n $N
