---------------------
Creating Wiki Subsets
---------------------


This project will create subsets of the wikipedia that will fit into a constrained size.

To use it:

    pip install -r requirements.txt  (may want to put this into a venv, up to you)
    python retrieve_files.py
    python generate_collections.py

The result will be a file named with the time of the trial.  In that file will be a top-N list of candidate
article sets, sorted by size, number of page links, number of language links, and page views.

Check the config file for various environment variables and configuration settings.  Some important ones:

    FTP_PASS: needed to download files from the kiwix site.  FTP_USER and FTP_SITE are already set by default.
    WHICH_WIKI: whether you want English, French, etc.  A complete list can be found on that FTP site.
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


To get a sorted list, invoke from the interpreter:

from info_prep import print_list_sorted_by_metric
print_list_sorted_by_metric()

To get the list of seeds, invoke from the interpreter:

from info_prep import get_seed_articles
seeds = get_seed_articles()
