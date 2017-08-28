const fs = require("fs");
const async = require("async");
const cheerio = require("cheerio");
const request = require("request");
const path = require("path");

const out = path.join(__dirname, "out/");
const wikiURL = "http://download.kiwix.org/wp1/";

function getFolderList() {
  return new Promise(resolve => {
    request("http://download.kiwix.org/wp1/", (err, response) => {
      const $ = cheerio.load(response.body);
      const langFolders = $("a");
      let langFoldersHrefs = [];
      langFolders.each((idx, folder) =>
        langFoldersHrefs.push(folder.attribs.href)
      );
      const filtered = filterFolders(langFoldersHrefs);
      resolve(filtered);
    });
  });
}

function filterFolders(folderList) {
  /* Takes an array of short href links (like "arwiki_2017-07/") and filters them
  so that we only work with the latest and greatest compilations */
  let bigList = [];
  let cleanedList = {};
  let exportList = [];

  // Clean cruft
  folderList.splice(0, 6);
  folderList.forEach(folder => {
    bigList.push(folder.split("_"));
  });

  // Use object to dedupe entries. Only the latest dates will survive
  bigList.forEach(item => {
    const storedDate = new Date(cleanedList[item[0]]);
    const nextDate = new Date(item[1]);
    if (!cleanedList.hasOwnProperty(item[0]) || storedDate < nextDate) {
      cleanedList[item[0]] = item[1];
    }
  });

  // reconstruct links from the cleanedList object. Ready for the dl process
  for (let keys in cleanedList)
    exportList.push(`${keys}_${cleanedList[keys]}`);
  return exportList;
}

function download(url, savePath, cb) {
  let received_bytes = 0;
  let total_bytes = 0;
  var req = request({
    method: "GET",
    uri: url
  });
  req.pipe(fs.createWriteStream(savePath));
  req.on("response", function(data) {
    total_bytes = parseInt(data.headers["content-length"]);
  });
  req.on("data", function(chunk) {
    received_bytes += chunk.length;
    const percentage = received_bytes * 100 / total_bytes;
    const filenameForLog = url.split("/");
    console.log(
      percentage.toFixed(2) +
        "% | " +
        parseInt(received_bytes / 1000) +
        "k of " +
        parseInt(total_bytes / 1000) +
        "k | " +
        filenameForLog[filenameForLog.length - 2] +
        "/" +
        filenameForLog[filenameForLog.length - 1]
    );
  });
  req.on("end", function() {
    cb();
  });
}

function downloadLanguagePack(link, packCB) {
  if (packCB === undefined) packCB = () => {};
  console.log("going to download " + link);
  const filenames = [
    "all.lzma",
    "langlinks.lzma",
    "pagelinks.lzma",
    "pages.lzma",
    "pageviews.lzma",
    "redirects.lzma"
  ];
  const folder = path.join(out, link);
  if (!fs.existsSync(folder)) fs.mkdirSync(folder);

  async.eachSeries(
    filenames,
    (filename, cb) => {
      const url = wikiURL + link + filename;
      const savePath = folder + filename;
      console.log(url, savePath);
      download(url, savePath, cb);
    },
    () => packCB()
  );
}

// ------- Main --------- //

if (process.argv.length === 4 && process.argv[2] === "--download") {
  getFolderList().then(folderList => {
    let choice = process.argv[3];
    if (choice[choice.length - 1] !== "/") choice += "/"; // Fix possible user typo
    folderList.indexOf(choice) !== -1
      ? downloadLanguagePack(choice)
      : console.log(
          `"${choice}" is not available as an option. Please check spelling`
        );
  });
} else if (process.argv.length === 3 && process.argv[2] === "--all") {
  getFolderList().then(availablePacks => {
    console.log("Starting the process of downloading all packs");
    async.eachSeries(availablePacks, (pack, cb) => {
      console.log("going to download ", pack);
      downloadLanguagePack(pack, cb);
    });
  });
} else {
  getFolderList().then(availablePacks => {
    console.log("Darkenvy's Kiwix Index Downloader");
    console.log("   --download [enwiki_2017-07]  :  Download a language pack");
    console.log("   --all                        :  Download all languages\n");
    console.log("List of available languages to download:");
    availablePacks.forEach(pack => console.log(pack));
  });
}
