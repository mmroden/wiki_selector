#!/bin/bash
zimwriterfs \
--title="ZimTest" \
--description="A quick test of zimwriterfs docker" \
--creator="Wikipedia Foundation" \
--publisher="Reno McKenzie" \
--tags="IIAB;Wikipedia" \
--language="en" \
--welcome="index.html" \
--favicon="favicon.ico" \
--withFullTextIndex \
/articles \
/output/$(date '+%Y-%m-%d_%H%M').zim

# Usage: zimwriterfs [mandatory arguments] [optional arguments] HTML_DIRECTORY ZIM_FILE

# Purpose:
# 	Packing all files (HTML/JS/CSS/JPEG/WEBM/...) belonging to a directory in a ZIM file.

# Mandatory arguments:
# 	-w, --welcome		path of default/main HTML page. The path must be relative to HTML_DIRECTORY.
# 	-f, --favicon		path of ZIM file favicon. The path must be relative to HTML_DIRECTORY and the image a 48x48 PNG.
# 	-l, --language		language code of the content in ISO639-3
# 	-t, --title		title of the ZIM file
# 	-d, --description	short description of the content
# 	-c, --creator		creator(s) of the content
# 	-p, --publisher		creator of the ZIM file itself

# 	HTML_DIRECTORY		is the path of the directory containing the HTML pages you want to put in the ZIM file,
# 	ZIM_FILE		is the path of the ZIM file you want to obtain.

# Optional arguments:
# 	-v, --verbose		print processing details on STDOUT
# 	-h, --help		print this help
# 	-m, --minChunkSize	number of bytes per ZIM cluster (defaul: 2048)
# 	-x, --inflateHtml	try to inflate HTML files before packing (*.html, *.htm, ...)
# 	-u, --uniqueNamespace	put everything in the same namespace 'A'. Might be necessary to avoid problems with dynamic/javascript data loading.
# 	-r, --redirects		path to the TSV file with the list of redirects (url, title, target_url tab separated).
# 	-i, --withFullTextIndex	index the content and add it to the ZIM.
# 	-a, --tags		tags - semicolon separated
# 	-n, --name		custom (version independent) identifier for the content

# Example:
# 	zimwriterfs --welcome=index.html --favicon=m/favicon.png --language=fra --title=foobar --description=mydescription \
# 		--creator=Wikipedia --publisher=Kiwix ./my_project_html_directory my_project.zim

# Documentation:
# 	zimwriterfs source code: http://www.openzim.org/wiki/Git
# 	ZIM format: http://www.openzim.org/