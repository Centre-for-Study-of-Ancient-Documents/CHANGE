
docker compose exec solr solr create -d /solr-conf -c foo 

export CORE=foo
./load-test.sh

