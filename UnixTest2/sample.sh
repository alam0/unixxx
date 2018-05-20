#!/bin/sh

N=5
S=cat
SF=""
while getopts n:S options; do
	case $options in
		n) N=$OPTARG ;;
		S) S=sort
			SF=-n ;;
	esac
done

shift $((OPTIND -  1))

shuf | head -n $N | $S $SF

