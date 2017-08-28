const gulp = require("gulp");
const gs = require("gulp-selectors");
const cleanCSS = require("gulp-clean-css");
const htmlmin = require("gulp-html-minifier");
const htmltidy = require("gulp-htmltidy");
const runSequence = require("run-sequence");
require("gulp-stats")(gulp);

const gsIgnores = {
  // ids: "cite_note-*",
  ids: "*", // If we don't ignore all IDs, anchor links breaks :(
  classes: "index-*"
};

const tidyOpts = {
  doctype: "html5",
  hideComments: true,
  indent: false
};

const cleanCssOpts = {
  compatibility: "ie7",
  rebase: true,
  rebaseTo: "/",
  level: {
    2: { all: true }
  }
};

const htmlMinOpts = {
  collapseWhitespace: false, // removes whitespace that is a part of text. Potential savings however
  collapseInlineTagWhitespace: true,
  collapseBooleanAttributes: true,
  decodeEntities: true,
  html5: true, // seems to break links when false
  minifyCSS: false, // uses cleanCSS which we have already done
  minifyURLs: true,
  keepClosingSlash: false,
  removeComments: true,
  removeEmptyAttributes: true,
  removeEmptyElements: true,
  removeOptionalTags: true,
  removeRedundantAttributes: true,
  removeScriptTypeAttributes: true,
  removeStyleLinkTypeAttributes: true,
  removeTagWhitespace: false, // will result in "invalid hmtl". But renders fine
  sortAttributes: true,
  useShortDoctype: true
};

gulp.task("clean-and-minify-css", () => {
  return gulp
    .src("./index.css") //
    .pipe(cleanCSS(cleanCssOpts)) //
    .pipe(gulp.dest("preprocessed_wiki_articles")); //
});

/* gs.run() normally breaks reference note anchors ( [33] => 33. ) 
However, with the GLOB selector for cite_note-*, restores some functionality */
gulp.task("joint-html-css-minify", () => {
  console.log(
    "Warning. You will get no status on this task. It will take a long time"
  );
  return gulp
    .src([
      "preprocessed_wiki_articles/index.css",
      "preprocessed_wiki_articles/**/*.html"
    ]) //
    .pipe(htmltidy(tidyOpts)) //
    .pipe(htmlmin(htmlMinOpts)) //
    .pipe(gs.run(undefined, gsIgnores)) // npmjs.com/package/gulp-selectors
    .pipe(gulp.dest("postprocessed_wiki_articles")); //
});

gulp.task("move-favicon", () => {
  gulp
    .src("./favicon.ico") //
    .pipe(gulp.dest("postprocessed_wiki_articles")); //
});

// ----------------------------------------------------------------- //

// gulp.task("default", ["clean-and-minify-css","joint-html-css-minify","move-favicon"]);
gulp.task("default", function(done) {
  runSequence(
    "clean-and-minify-css",
    "joint-html-css-minify",
    "move-favicon",
    () => done
  );
});

/* Consider splitting "joint-html-css-minify" into multiple tasks. I 
dont want files to be overwritten in place however and this would make a
mess requiring another folder. */
