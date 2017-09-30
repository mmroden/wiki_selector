const async = require("async");
const path = require("path");
const download = require("download");
const fs = require("graceful-fs");
const { loadListFile, cleanUrl, getFilename, prependUrl } = require("./_helper");
const { WIKI_LIST, CONCURRENT_CONNECTIONS, SAVE_PATH, WIKI_DL } = require("./config");

function massDownloadImages(imageSources) {
  function processImage(url, callback) {
    logCounter++;
    let dlUrl = cleanUrl(url);
    dlUrl = prependUrl(dlUrl);

    let filename = getFilename(url);
    filename = filename.split("?")[0]; // get rid of query parameters on the filename
    try {
      filename = decodeURI(filename);
    } catch (e) {
      console.log("Malformed URL. Skipping image", url);
      return;
    }

    const saveLocation = path.join(SAVE_PATH, filename);
    fs.access(saveLocation, fs.constants.F_OK, doesntExist => {
      if (doesntExist) {
        downloadImage(dlUrl, filename, saveLocation, callback);
      } else {
        console.log("skipping", filename);
        callback();
      }
    });
  }

  function downloadImage(url, filename, saveLocation, callback) {
    console.log(`${logCounter}/${imageList.length} | downloading ${filename}`);
    download(url).then(data => fs.writeFile(saveLocation, data, callback)).catch(err => {
      // Push image back on the queue if it is a 429 (too many requests)
      if (err.statusCode === 429) {
        console.log("pushing", filename, "back on the queue");
        queue.push(url);
      }
      console.log("   ", err.statusCode, filename);

      // Write error out to file
      const ERR_FILE = path.join(__dirname, "missing_images.txt");
      fs.appendFile(ERR_FILE, `${err.statusCode} ${url}\n`, err => {
        if (err) console.log("problems appending to error file", err);
        callback();
      });
    });
  }

  let logCounter = 0;
  const imageList = Object.keys(imageSources);
  const queue = async.queue(processImage, CONCURRENT_CONNECTIONS);
  queue.push(imageList);
  queue.drain = () => {
    console.log("All Images Downloaded");
  };
}

function gatherImageList(zimList) {
  const imageSources = {};
  let logCounter = 0;

  function processHtmlFile(filename, callback) {
    console.log(`${logCounter}/${zimList.length} | processing html ${filename}`);
    /* Load HTML from file, use Cheerio (like jQuery) to find all
    image tags. Take the src and add it to the master list of imageSources */
    const htmlFilePath = path.join(WIKI_DL, filename + ".html");
    fs.readFile(htmlFilePath, "utf8", (err, html) => {
      logCounter++;
      if (err) {
        callback();
        return;
      }
      /* I am not replacing anything (the replace function doesn't mutate but 
      returns a new object). I am using this because the replace method allows
      for the g flag. exec does not. Kind of a hack in the name of science! */
      html.replace(/img.+?src="(.+?)"/g, (m, a) => imageSources[a] = 1);
      callback();
    });
  }

  const fileQueue = async.queue(processHtmlFile, CONCURRENT_CONNECTIONS);
  fileQueue.push(zimList);
  fileQueue.drain = () => {
    console.log("All html files parsed for images");
    massDownloadImages(imageSources);
  };
}

// --------- Init --------- //
/* Load up all the html files, find the image links, add to list,
then download each image (only if not found locally */

// Create image folder if not exist
fs.access(SAVE_PATH, fs.constants.F_OK, doesntExist => {
  if (doesntExist) fs.mkdirSync(SAVE_PATH);
});

console.log("Loading list");
loadListFile(WIKI_LIST).then(zimList => {
  console.log("List loaded. Starting to open html and seek image links");
  gatherImageList(zimList);
});
// gatherImageList(["ABBA"]);
