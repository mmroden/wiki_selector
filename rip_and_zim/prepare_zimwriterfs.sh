#!/bin/bash
cp favicon.ico processed_wiki_articles/
cp index.css processed_wiki_articles/
cp angular.min.js processed_wiki_articles/
cp index.html processed_wiki_articles/
# find raw_wiki_articles/images -regex ".*[^.]...$" -exec "cp {} processed_wiki_articles/images/{} \;"
echo "Done Copying favicon html css and angular into processed_wiki_articles folder"