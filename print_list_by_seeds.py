from info_prep import (get_seed_articles, print_collection, prepare_seeded_set)
import config

"""
This quick file will print out the list of articles sorted via Martin's score generator.
It uses the config settings to determine the cutoff by size.
"""

def main():
    seeds, all_articles = get_seed_articles()
    list_name = "Seed_List_{}.txt".format(config.which_wiki)
    print_collection(seeds, all_articles, list_name)
    prepare_seeded_set(seeds, all_articles)


if __name__ == "__main__":
    main()
