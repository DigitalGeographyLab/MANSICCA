#!/bin/bash

url="${1}"
pgconn="${2}"
table="${3}"


wd="$(realpath $(dirname "${0}"))"

display_url="$(wget "${url}" -qO - |grep display_url|sed 's/.*"display_url": "\([^"]*\)",.*/\1/')"

if [[ -n "$display_url" ]]; then

    photo="$(echo ${url} | sed 's/^.*\/\([^\/]*\)\/$/\1/')"

    if [[ -e "${wd}/images/${photo}.jpg" ]]; then
        echo -n "*"
    else
        wget -cqO "${wd}/images/${photo}.jpg" "${display_url}"
    echo -n "+"
    fi

    echo "update ${table} set photo='${photo}.jpg' where url='${url}'" | psql -t "${pgconn}" -q

else
    echo "update ${table} set photo='[none]' where url='${url}'" | psql -t "${pgconn}" -q
    echo -n "-"
fi
