#! /bin/bash

CORE="${CORE:-foo}"
DATA=ionia.xml

echo Uploading ${DATA} to core ${CORE}

curl http://localhost:8983/solr/${CORE}/update -H "Content-Type: text/xml" \
	--data @ionia.xml

curl http://localhost:8983/solr/${CORE}/update -H "Content-Type: text/xml" \
	--data '<commit/>'
