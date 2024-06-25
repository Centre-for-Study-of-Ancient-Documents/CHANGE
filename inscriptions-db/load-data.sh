#! /bin/bash

BASE="20240528"

CORE="${CORE:-inscriptions}"
# Use argument as BASE if given
BASE="${1:-$BASE}"

#DATA=data/20231003.Mysia_Troad_Aiolis_Lesbos.xml
#DATA2=data/20231003.Ionia.xml

echo Loading data starting with \`${BASE}\' to core ${CORE}
echo
echo Found $(ls -d "data/${BASE}".* | wc -l) files
echo

for d in "data/${BASE}."* ; do
	echo Loading ${d}:
	curl http://localhost:8983/solr/${CORE}/update -H "Content-Type: text/xml" \
		--data "@$d"
	echo
done

echo Committing data:
echo

curl http://localhost:8983/solr/${CORE}/update -H "Content-Type: text/xml" \
	--data '<commit/>'

