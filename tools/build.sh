#!/usr/bin/env bash

baseDir="$(realpath "$(dirname "${0}")/..")"
cd "${baseDir}"

minify=true
uploadToTestServer=false
uploadToProductionServer=false
createZipArchive=false
for arg in "$@"; do
    echo "$arg"
    if [[ "$arg" == "-M" ]]; then
       minify=false
    fi
    if [[ "$arg" == "-t" ]]; then
       uploadToTestServer=true
    fi
    if [[ "$arg" == "-p" ]];then
       uploadToProductionServer=true
    fi
    if [[ "$arg" == "-z" ]];then
        createZipArchive=true
    fi
done


# -- 
#    minify script/stylesheets, 
#    upload to testserver, 
#    create zipfile


# -- 0) have a tmp dir for all in-between stuff
tempDir="$(mktemp -d)"


# -- 1) prepare build dir
rsync -avzH --progress --partial --delete \
    --exclude '***/.keep' \
    --exclude '***/.DS_Store' \
    --exclude '***.swp' \
    "${baseDir}/src/"    \
    "${baseDir}/build/"

cd build

# -- 2) minify javascript
if $minify; then
    find . -iname "*.js" -and -not -iname "*.min.js" | while read jsFile;do
        uglifyjs -c -m -o "${jsFile/%.js/.min.js}" "${jsFile}" &&
            find . \( -iname "*.html" -or -iname "*.php" \) -exec sed -i "s/$(basename ${jsFile})/$(basename ${jsFile/%.js/.min.js})/g" {} \; &&
                rm -v "${jsFile}"
    done
fi


# -- 3) minify stylesheets
if $minify; then
    find . -iname "*.css" -and -not -iname "*.min.css" | while read cssFile;do
        csso -i "${cssFile}" -o "${cssFile/%.css/.min.css}" &&
            find . \( -iname "*.html" -or -iname "*.php" \) -exec sed -i "s/$(basename ${cssFile})/$(basename ${cssFile/%.css/.min.css})/g" {} \; &&
                rm -v "${cssFile}"
    done
fi

cd "${baseDir}"


# -- 4) upload to test server
if $uploadToTestServer; then
    rsync -avzH --progress --delete --partial \
        --exclude '***/.keep' \
        --exclude '***/.DS_Store' \
        --exclude '***.swp' \
        --exclude 'assets/data/***' \
        build/ \
        christoph@chri.stoph.at:/var/www/musticca.christophfink.com/htdocs-secure/
fi;


# -- 5) upload to production server
if $uploadToProductionServer; then
    echo "no production server defined"
#    read -r -p "upload to PRODUCTION? [y/N] " response
#    response=${response,,}    # tolower
#    if [[ "$response" =~ ^(yes|y)$ ]]; then
#        rsync -avzH --progress --delete --partial \
#            --exclude '***/.keep' \
#            --exclude '***/.DS_Store' \
#            --exclude '***.swp' \
#            build/ \
#            porem@upload.univie.ac.at:/u/www/porem/maps/
#    fi
fi


# -- 6) create zip archive 
if $createZipArchive; then
    cd "${baseDir}"
    zipFileName="$(date +"mansicca_%Y%m%d")"
    ln -s build "${zipFileName}"
    zip -r "${zipFileName}" "${zipFileName}"
    mv "${zipFileName}.zip" ~/Downloads/
    rm "${zipFileName}"
fi


# -- 999) delete tmp dir!
rm -Rf "${tempDir}"
