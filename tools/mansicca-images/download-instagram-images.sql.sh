#!/bin/bash

table="instagram_southafrica"
pgconn="dbname=mansicca"


wd="$(realpath $(dirname "${0}"))"
mkdir -p "${wd}/images/"

(
psql -t "$pgconn" << EOSQL
    select url from ${table} where photo='';
EOSQL
) | xargs -P 10 -I {} "${wd}/download-one-instagram-image.sh" "{}" "${pgconn}" "${table}"
