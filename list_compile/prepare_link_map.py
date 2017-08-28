from info_prep import resolve_all_links_and_redirects
import pickle
import os
import config

"""
This file will prepare the set of all links across all articles.
Note that this list will not respect inclusions and exclusions;
subsequent seeding attempts will need to use those directly for filtering
the growing seed set.

The results are saved as a pickle for ease of use in other python
programs, and may not be appropriate for cross-language use.
"""

def main():
    if config.testing:
        print ("Running in testing mode, will produce a smaller file faster.")
    else:
        print ("Running in production mode, will produce the full file.")
    link_map = resolve_all_links_and_redirects()
    with open(os.path.join(config.which_wiki, 'link_map.pkl'), 'wb') as link_file:
        pickle.dump(link_map, link_file)

        
if __name__ == "__main__":
    main()
