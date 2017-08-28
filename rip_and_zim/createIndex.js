const async = require("async");
const path = require("path");
const download = require("download");
const cheerio = require("cheerio");
const fs = require("graceful-fs");
const { loadListFile } = require("./_helper");
const { WIKI_LIST, PROCESSED_WIKI_DL } = require("./config");

function generateIndex(indexList) {
  console.log("Starting to generate list");
  let logCounter = 0;

  const indexPagePath = path.join(PROCESSED_WIKI_DL, "index.html");
  const title = "Hello World";
  const head = `
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <meta http-equiv="X-UA-Compatible" content="ie=edge">
      <title>${title}</title>
      <link rel="stylesheet" href="index.css" />
    </head>
    <body class="index-body">
      <ul class="index-container">
  `;
  const foot = `
      </ul>
    </body>
    </html>
  `;

  // Overwrite if exists, and start fresh with the head
  fs.writeFileSync(indexPagePath, head);

  // create a entry for each item in the list
  indexList.forEach(item => {
    console.log(`${logCounter}/${indexList.length} | Processing ${item}`);
    logCounter++;

    const $li = `<li><a href="${item}.html">${item.replace("_", " ")}</a></li>`;
    fs.appendFileSync(indexPagePath, $li);
  });

  fs.appendFileSync(indexPagePath, foot);
  console.log("Done");
}

console.log("Loading list of processed files");
let processedFiles = fs.readdir(PROCESSED_WIKI_DL, (err, files) => {
  if (err) {
    console.log("Fatal error: Cannot read directory");
    return;
  }
  let fileList = files.filter(file => /\.html/.test(file));
  fileList = fileList.map(file => file.split(".").slice(0, -1)[0]);
  fileList = fileList.filter(file => !/index/.test(file));

  // Removes duplicates like "Acre" and "Acre_"
  console.log("Removing duplicates");
  const dupRemover = {};
  fileList.forEach(file => {
    if (file[file.length - 1] === "_") dupRemover[file.slice(0, -1)] = 1;
    else dupRemover[file] = 1;
  });

  // generateIndex(fileList);
  generateIndex(Object.keys(dupRemover));
});
