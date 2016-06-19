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

Check the config file for various environment variables and configuration settings.

Note that this process takes a _very_ long time to run.

TODO:
1.  Add in quality and importance metrics.  This is trickier than it might seem at first glance.
2.  Multiprocessing is a terrible memory hog right now; I would recommend not using it.
3.  The output is less than useful in its current incarnation.
