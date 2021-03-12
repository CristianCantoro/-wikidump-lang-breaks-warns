#!/bin/bash

# Requirements: https://github.com/CristianCantoro/wikidump-download-tools
# You must have cloned this repository on your computer

# Find wikidumps download tools in your file system
WIKI_DUMP=$(find ~ -type d -name "wikidump-download-tools" -print -quit)

# For now only italian, catalan, spanish and english dumps dated 2021-02-01
dates=( 20210201 )
langs=( it ca es en )

echo "Start the download"

# Call for each date and for each lang the download tool, start the download
for i in "${dates[@]}"; do
    for j in "${langs[@]}"; do
        echo "Downloading ${j}wiki dated ${i}"
        $WIKI_DUMP/scripts/wikidump-download.sh "https://dumps.wikimedia.org/${j}wiki/${i}"
        mkdir -p "../dumps/${j}wiki/${i}"
        ln -s "./data/${j}wiki/${i}/*" "../dumps/${j}wiki/${i}/"
    done
done

rm *.log

echo "Download done"
