from info_prep import (get_seed_articles, print_collection, calculate_article_score)
import config
import pickle
import os

"""
This code will first read in the link map, if it exists, or creates it, if it does not.
From that, the seed articles can be grown.
"""

def read_link_map():
    try:
        with open(os.path.join(config.which_wiki, 'link_map.pkl'), 'rb') as link_file:
            link_map = pickle.load(link_file)
    except:
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
    current_scores = [(article_id, calculate_article_score(all_articles[article_id]))
                      for article_id in seeds]
    seed_score = sum(entry[1] for entry in current_scores)
    growing = seed_score > config.target_size
    print ("Current size: {} Target size: {} growing: {}".format(seed_score, config.target_size, growing))
    while growing:
        # get links by seed
        new_set = set()  # set of article ids
        new_article_scores = []  # set of article tuples
        for seed in current_seeds:
            new_set.add(tuple(id for id in link_map[int(seed)]))
        new_article_scores = [(article_id, calculate_article_score(all_articles[article_id]))
                              for article_id in new_set]
        score_sum = sum(entry[1] for entry in new_article_scores)
        if score_sum + seed_score > config.target_size:
            print ("Hit size limit, truncating current set of candidate articles.")
        else:
            print ("Size limit not hit, growing further out.")
            current_seeds = current_seeds.union(new_set)
            seed_score = score_sum + seed_score
    return current_seeds


def main():
    link_map = read_link_map()
    seeds, all_articles = get_seed_articles()
    list_name = "Seed_List_{}.txt".format(config.which_wiki)
    print_collection(seeds, all_articles, list_name)
    grown_seeds = grow_seeds(seeds, all_articles, link_map)
    grown_list_name = "Grown_Seed_List_{}.txt".format(config.which_wiki)
    print_collection(grown_seeds, all_articles, grown_list_name)


if __name__ == "__main__":
    main()
