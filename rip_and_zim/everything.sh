#!/bin/bash
# Run every command in order. I see a hang at the end of pullArticles. One off bug?
./prep.sh
node pullArticles.js
node pullImages.js
node processArticles.js
node processImages.js
node createIndex.js
./prepare_zimwriterfs.sh
./zimwriterfs.sh