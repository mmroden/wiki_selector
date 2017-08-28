const async = require("async");
const path = require("path");
const download = require("download");
const fs = require("graceful-fs");
const { loadListFile } = require("./_helper");
const {
  CONCURRENT_CONNECTIONS,
  WIKI_DL,
  MEDIA_WIKI,
  WIKI_LIST,
  LOG_MISSING
} = require("./config");

/* --- Notes about imports --- 
I am using the module graceful-fs which patches fs to fix problems with 
concurrent-open-file-limits. fs seems to not close files soon enough and
causes a race condition. Lets see if we can remove it as time goes on.

Only ever saw this error when writing 54k empty files at once (using 
async concurrency of 1)
*/

function downloadWikiArticles(articleListArr) {
  function processArticle(article, callback) {
    /* Check for file access. If the process returns an error, this means
    the file doesn't exist. So lets download the article! Otherwise, skip */
    logCounter++;
    const filePath = path.join(WIKI_DL, article + ".html");
    fs.access(filePath, fs.constants.R_OK, err => {
      if (err)
        console.log(
          `${logCounter}/${articleListArr.length} | downloading ${article}`
        );
      else console.log("skipping", article);
      err ? getArticle(article, callback) : callback();
    });
  }

  // Do the actual downloading
  function getArticle(article, callback) {
    const url = MEDIA_WIKI + article;
    const filePath = path.join(WIKI_DL, article + ".html");
    download(url)
      .then(html => fs.writeFile(filePath, html, callback))
      .catch(err => {
        // Push article back on the queue if it is a 429 (too many requests)
        if (err.statusCode === 429) {
          console.log("pushing", article, "back on the queue");
          queue.push(article);
        }
        console.log("   ", err.statusCode, article);

        // Write error out to file
        if (LOG_MISSING) {
          const ERR_FILE = path.join(__dirname, "missing_articles.txt");
          fs.appendFile(ERR_FILE, `${err.statusCode} ${article}\n`, err => {
            if (err) console.log("problems appending to error file", err);
            callback();
          });
        } else {
          callback();
        }
      });
  }

  /* Initialize a queue that limits concurrent downloads. The queue will 
  automatically start processing. Upon finish, the drain function will run */
  let logCounter = 0;
  const queue = async.queue(processArticle, CONCURRENT_CONNECTIONS);
  queue.push(articleListArr);
  queue.drain = () => {
    console.log("All articles downloaded");
  };
}

// ---------- Init ---------- //

loadListFile(WIKI_LIST).then(downloadWikiArticles);
