from info_prep import (get_seed_articles, print_collection,
                       calculate_article_score, resolve_all_links_and_redirects)
import config
import pickle
import os

"""
This code will first read in the link map, if it exists, or creates it, if it does not.
From that, the seed articles can be grown.
"""

def read_link_map():
    try:
        print ("Reading in the link map.")
        with open(os.path.join(config.which_wiki, 'link_map.pkl'), 'rb') as link_file:
            link_map = pickle.load(link_file)
    except:
        print ("Reading in the link map failed, recreating it.")
        link_map = resolve_all_links_and_redirects()
        with open(os.path.join(config.which_wiki, 'link_map.pkl'), 'wb') as link_file:
            pickle.dump(link_map, link_file)
    return link_map


def grow_seeds(seeds, all_articles, link_map):
    '''
    Given a set of seeds, all_articles, and link_map, grow the seeds according to links
    The growth will be up to the configured size, truncating the addition.
    '''
    current_seeds = seeds
    current_size = sum(all_articles[article_id][2] for article_id in seeds)
    growing = current_size < config.target_size
    print ("Current size: {} Target size: {} growing: {}".format(current_size, config.target_size, growing))
    while growing:
        # get links by seed
        new_set = set()  # set of article ids
        new_article_scores = []  # set of article tuples
        for seed in current_seeds:
            if int(seed) in link_map:
                new_set.add(id for id in link_map[int(seed)])
            else:
                print("Unable to grow from seed {}".format(int(seed)))
        size_sum = sum(all_articles[entry][2] for entry in new_set)
        print("Expanded set size: {}".format(size_sum))
        if size_sum + current_size > config.target_size:
            print ("Hit size limit, truncating current set of candidate articles.")
        else:
            print ("Size limit not hit, growing further out.")
            current_seeds = current_seeds.union(new_set)
            seed_score = size_sum + current_size
    return current_seeds


def main():
    link_map = read_link_map()
    print ("Link map has been loaded, generating seeds.")
    seeds, all_articles = get_seed_articles()
    list_name = "Seed_List_{}.txt".format(config.which_wiki)
    print_collection(seeds, all_articles, list_name)
    print ("Initial seed list saved, growing seeds.")
    grown_seeds = grow_seeds(seeds, all_articles, link_map)
    grown_list_name = "Grown_Seed_List_{}.txt".format(config.which_wiki)
    print_collection(grown_seeds, all_articles, grown_list_name)
    print ("Seeds grown, ending.")


if __name__ == "__main__":
    main()
