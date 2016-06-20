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
2.  Multiprocessing is a terrible memory hog right now; I would recommend using it very sparingly.
3.  The output is less than useful in its current incarnation.

On my system, I am running this setup right now with

    python -m scoop -n 3 generate_collections.py

I have a core i7 with 4 real cores and 4 hyperthreaded cores, as well as 16 gb of RAM-- memory spikes to 13 gb
during setup, and then stabilizes to around 60%.  This is Windows 10.

