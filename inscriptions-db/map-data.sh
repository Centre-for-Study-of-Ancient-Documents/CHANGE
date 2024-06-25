#! /bin/bash

BASE="20240528"
OUTDIR="data"

# Use argument as BASE if given
BASE="${1:-$BASE}"

echo Mapping CSV files in instance/ starting with ${BASE} 
echo output to ${OUTDIR}/
echo
echo Found $(ls -d "instance/${BASE}".*.csv | wc -l) files
echo

INDEX=0
for D in "instance/${BASE}."*.csv ; do
	echo Mapping: ${D}:
	D2="${D%csv}"
	OUT="data/${D2#instance/}xml"
	if [ -e "$OUT" ] ; then
		echo Existing file: ${OUT}
		echo Moving file
		mv $OUT "data/old.${D2#instance/}xml"
	fi
	INDEX=$((INDEX+1))
	docker compose exec web flask index-csv -s $(printf "%02d" $INDEX) $D >$OUT
	echo
done

