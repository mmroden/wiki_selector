const path = require("path");

function loadListFile(filename) {
  /* We must load in the list to be processed before downloading */
  return new Promise(resolve => {
    const wikiList = [];
    const lineReader = require("readline").createInterface({
      input: require("fs").createReadStream(
        path.join(__dirname, "selections", filename)
      )
    });

    lineReader.on("line", line => wikiList.push(line));
    lineReader.on("close", () => resolve(wikiList));
  });
}

const cleanListOfLinks = linkArr => {
  let linkList = linkArr;
  linkList = linkList.filter(url => {
    if (!url) return false;
    else if (url[0] === "#") return false;
    else if (/https?:\/\/.+wiki/g.test(url)) return true;
    else if (/https?:\/\//g.test(url)) return false;
    else if (/index.php/g.test(url)) return false;
    else if (/action=edit/g.test(url)) return false;
    else if (/^\/\//.test(url)) return false;
    return true;
    // else if (/File:/g.test(url)) return false; // Removes potential pictures see: https://en.wikipedia.org/wiki/ASCII
  });
  linkList = linkList.map(url => decodeURI(url));
  linkList = linkList.map(url => url.replace(/^\/wiki\//, ""));
  linkList = linkList.map(url => url.split("?")[0]); // get rid of parameters eg: ?action=submit
  return linkList;
};

const getFilename = url => decodeURI(url.split("/").slice(-1)[0]);
const cleanUrl = url => {
  let newUrl = url;
  while (newUrl[0] === "/")
    newUrl = newUrl.slice(1);
  return newUrl;
};
const prependUrl = url => {
  if (/static\//.test(url)) return `https://wikipedia.org/${url}`;
  else return url;
};

module.exports = {
  loadListFile,
  cleanUrl,
  getFilename,
  cleanListOfLinks,
  prependUrl,
  cssIds,
  cssClasses
};
