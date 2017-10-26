#!/bin/bash

url="${1}"
pgconn="${2}"
table="${3}"


wd="$(realpath "$(dirname "${0}")")"

index="$(mktemp)";

wget "${url}" -q -O "${index}"

display_url="$(cat "${index}" |grep display_url|sed 's/.*"display_url": "\([^"]*\)",.*/\1/')"
if [[ -n "$display_url" ]]; then

    photo="$(echo ${url} | sed 's/^.*\/\([^\/]*\)\/$/\1/')"
    d="$(echo "${photo}" | cut -c1)"
    mkdir -p "${wd}/images/${d}/"

    if [[ -e "${wd}/images/${d}/${photo}.jpg" ]]; then
        echo -n "*"
    else
        wget -cqO "${wd}/images/${d}/${photo}.jpg" "${display_url}"
        echo -n "+"
    fi

    echo "update ${table} set photo='${photo}.jpg' where url='${url}'" | psql -t "${pgconn}" -q

else
    echo "update ${table} set photo='[none]' where url='${url}'" | psql -t "${pgconn}" -q
    #echo -n "-"
fi

caption="$(cat "${index}" | grep "window._sharedData" | sed 's/^.*window._sharedData = \({.*}\)[^}]*$/\1/g'|json_reformat | grep -A 6 edge_media_to_caption|grep '"text":' | sed 's/^.*"text": "\(.*\)"$/\1/' | sed "s/'/''/g")"
echo "update ${table} set caption='${caption}' where url='${url}';" | psql -t "${pgconn}" -q

rm -f "${index}"
