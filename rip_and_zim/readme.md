# mwOffnet
An optimized way to download a MediaWiki

Edit `config.js` to reference your wiki_list.lst file path (which will be inside selections/)

You can delete `missing_*.txt` at any time. It is for your reference to `tail -f`.

## One time install
 * sudo apt-get install imagemagick graphicsmagick
 * npm install

## Before every build
  1. Edit the first 3 lines of config.js to specify a article selection list, wikipedia language and concurrent downloads (8 default).
  2. Edit zimwriterfs_config/boot.sh for the metadata of the zim you will produce. This information is shown on the main menu of kiwix-serve so this step is important!
  3. Update zimwriterfs_config/Dockerfile line 55 to force cache invalidation. Docker likes to cache docker images, which if not invalidated will contain a old boot.sh metadata file. Simply changing this line will force Docker to rebuild from that step onward.

## Order of operations
  1. ./prep.sh
  2. node pullArticles.js
  3. node pullImages.js
  4. node processArticles.js
  6. node processImages.js
  7. node createIndex.js
  8. ./prepare_zimwriterfs.sh
  8. ./zimwriterfs.sh
  9. Profit??

## What everything does
  * prep.sh creates the nessisary folder/subfolders and files needed for the process. Further scripts need not to check if the folders are in place.
  * pullArticles will look at config.js for the filename of a selection list. It will then  download a article from the specified wikipedia. eg: es.wikipedia.org, en.wikipedia.org
  * pullImages will reach each article html file that was pulled down from the previous step, and find all sources of images. It will then proceed to download each image.
  * processArticles will use a new folder (as not not disturb the raw downloaded files) and will clean up each article html file. This way, links are adjusted and removed if not used.
  * processImages will also use the new folder (to not disturb the original downloads) and convert each image using imageMagick/graphicsMagick to save space.
  * createIndex will compile a list of all articles in the converted folder and assemble a javascript file for use on the index page. The index.html page is a Angular file that lists every article in a table of contents. Without createIndex, Angular will not know what articles exist.
  * prepare_zimwriterfs moves the index.html page, css files and the favicon into place as required by zimwriterfs. zimwriterfs will not work without specific requirements like favicon and index.html
  * zimwriterfs will spin up a docker image, mount our prepared folder, and spit out a zim in the out folder. A 8GB wikipedia zim takes about 6 hours on a NUC during this process.

## Todo
  * Add timeout for when a 'too fast' statuscode appears.

## Known Problems
  * ~processImages can't handle 32755 encodings on a NUC. Claims 'too many files open'. Fixed on OSX by using graceful-fs but still broken on linux.~