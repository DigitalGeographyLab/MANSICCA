#!/bin/bash

table="instagram_sa_visitorhistory"
pgconn="dbname=chrisfin"


wd="$(realpath "$(dirname "${0}")")"
mkdir -p "${wd}/images/"

(
psql -t "$pgconn" << EOSQL
    select url from ${table} where caption='-1' or photo='';
EOSQL
) | xargs -P 10 -I {} "${wd}/download-one-instagram-image.sh" "{}" "${pgconn}" "${table}"
