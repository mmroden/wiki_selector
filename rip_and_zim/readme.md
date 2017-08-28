# mwOffnet
An optimized way to download a MediaWiki

Edit `config.js` to reference your wiki_list.lst file path (which will be inside selections/)

You can delete `missing_*.txt` at any time. It is for your reference to `tail -f`.

## One time install
 * sudo apt-get install imagemagick graphicsmagick
 * npm install

## Order of operations
  1. ./prep.sh
  2. node pullArticles.js
  3. node pullImages.js
  4. node processArticles.js
  6. node processImages.js
  7. node createIndex.js
  8. ./zimwriterfs.sh
  9. Profit??

## Multitasking
After you successfully `node pullArticles`, you can `node pullImages.js` at the same time as `node crossReferenceLinks.js`. 

`node crossReferenceLinks.js` can be done at the same time as `node processImages`.

`node processImages.js` can be done at the same time as `node creatIndex.js`

Do note however, that some tasks are internet hungry and others and cpu hungry. If you multitask two at the same time, they may fight for resources.

## Todo
  * Add timeout for when a 'too fast' statuscode appears.

## Known Problems
  * ~processImages can't handle 32755 encodings on a NUC. Claims 'too many files open'. Fixed on OSX by using graceful-fs but still broken on linux.~