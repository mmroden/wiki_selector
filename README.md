---------------------
Creating Wiki Subsets
---------------------


This project will create subsets of the Wikipedia that will fit into a constrained size.

This repo requires python3!  Having said that, you do _not_ need to create a venv with
requirements.txt unless you want to experiment with using genetic algorithms for subselection
creation, which is a very ambitious project that has yet to bear fruit, as of Oct 2016.

There are two basic ways to run it right now.  Before you do either, you will need a copy of
the wikipedia metadata.  That metadata is available on the kiwix ftp serviers, and you can
download it by using the retrieve_files.py file:

    python3 retrieve_files.py

Please note that you will need to set these environment variables:

    FTP_PASS: needed to download files from the kiwix site.  FTP_USER and FTP_SITE are already set by default.
    WHICH_WIKI: whether you want English, French, etc.  A complete list can be found on that FTP site.

(Why environment variables, and not some other way of passing parameters?  Using environment variables
as a configuration system is a pattern that I'm using elsewhere to great effect with Docker-based image
deploys via Rancher.  It may not be the Right Thing to do here, but it is easy, I'm familiar with
it, and it works.)

The simple, simple way is to run print_list_by_score.py:

    python3 print_list_by_score.py

The variables this script pays attention to:

    excluded_projects: a list of projects that you want to exclude from the subset.  Configured
        by editing config.py.
    SIZE: the target size of your final output, in bytes.

What it does:

    Goes through the complete page list
    Removes pages that have been tagged with excluded projects
    Scores all pages according to the 0.7 score metric
    Sorts all pages
    Produces the list of pages sorted by scores and truncated to the provided target size

A less simple way to run this is to run print_list_by_seeds.py:

    python3 print_list_by_seeds.py

This script will create a seed of emphasized projects, and then grow from that seed to connected
articles until the size limit is reached.  When the size is exceeded, higher scoring articles take
precedence.  This script uses the parameters for print_list_by_score.py, as well as:

    EMPHASIZED_PROJECTS: a list of projects that you want to include in your subset.  Easily configured
        by editing the _default_projects_ parameter in config.py.
    MIN_EMPH: the number of articles to include from each of the emphasized project for the starting
        seed.

There is also code in there for doing list generation by genetic algorithms.  This code is not yet ready
for prime time, and should probably be avoided.

To use it:

    virtualenv venv (to run inside a venv; again, this requires python3, so make sure you're making the right venv)
    pip install -r requirements.txt  (may want to put this into a venv, up to you)
    python retrieve_files.py
    python generate_collections.py

The result will be a file named with the time of the trial.  In that file will be a top-N list of candidate
article sets, sorted by size, number of page links, number of language links, and page views.

Check the config file for various environment variables and configuration settings.  Some important ones:


    MAX_NUM_SETS: the number of wiki subsets to report for each prioritization type
    SIZE: the target size of the wiki collection in bytes, using the size provided in the all.lzma file

Note that this process takes a _very_ long time to run.

TODO:

1.  Add in quality and importance metrics.  This is trickier than it might seem at first glance.
2.  Multiprocessing is a terrible memory hog right now; I would recommend using it very sparingly, if at all
3.  The output is less than useful in its current incarnation.

To run with multiprocessing:

    python -m scoop -n N generate_collections.py

where _N_ is the number of cores you want to use for this process.  When N > 2, the memory needs are
so large that, on Windows 10 at least, disk swap needs to be engaged.  At that point, the speed of
using more cores is probably outweighed by hitting the disk.


To get a sorted list, invoke from the command line:

python print_list_by_score.py

To get the list of seed articles, invoke from the interpreter:

python print_list_by_seeds.py
