"""This example shows a possible answer to a problem that can be found in this
xkcd comics: http://xkcd.com/287/. In the comic, the characters want to get
exactly 15.05$ worth of appetizers, as fast as possible."""
import random
from operator import attrgetter
from collections import Counter
from operator import itemgetter
from info_prep import prep_files, min_array, ranges
import config
from scoop import futures  # to make things multicore
import numpy as np
import pickle

# We delete the reduction function of the Counter because it doesn't copy added
# attributes. Because we create a class that inherit from the Counter, the
# fitness attribute was not copied by the deepcopy.
# del Counter.__reduce__

import numpy

from deap import algorithms
from deap import base
from deap import creator
from deap import tools
import time


# -------------------------
# Dummy data functions, for testing/debugging GA functions
# -------------------------

def create_dummy_data_fast():
    """
    for testing purposes and rapid iteration, make a structure similar to all_pages
    but just not as big.  Helps with debugging what happens after files are loaded
    """
    dummy_wiki_size = 500
    dummy_wiki = {}
    for i in range(dummy_wiki_size):
        idx = i * 100
        dummy_wiki[idx] = (idx, "dummy{}".format(idx), random.randint(0,100),
                           random.randint(0,100), random.randint(0,100),
                           random.randint(0,100))
    return dummy_wiki


# --------------------------
# calling in prepped data
# --------------------------

ALL_FILES = prep_files()  # create_dummy_data_fast()  # prep_files()
ALL_FILES_KEYS = list(ALL_FILES.keys())
ALL_FILES_KEYSET = set(ALL_FILES_KEYS)
ALL_FILES_SIZE = len(ALL_FILES_KEYS)
PAGE_LINKS_INDEX = 3
LANG_LINKS_INDEX = 4
PAGE_VIEWS_INDEX = 5
PAGE_SIZE_INDEX = 2
PAGE_TITLE_INDEX = 0
QUALITY_INDEX = 6
IMPORTANCE_INDEX = 7

QUAL_RATIO = 0.4
IMPT_RATIO = 0.4

ALL_FILES_HI_Q_KEYS = list(entry for entry in ALL_FILES_KEYS if ALL_FILES[entry][QUALITY_INDEX] > 0)
ALL_FILES_HI_I_KEYS = list(entry for entry in ALL_FILES_KEYS if ALL_FILES[entry][IMPORTANCE_INDEX] > 0)


# ----------------------------
# GA functions
# ----------------------------

creator.create("Fitness", base.Fitness, weights=(-1.0, 1.0, 1.0, 1.0, 1.0, 1.0))
creator.create("ArticleSet", list, fitness=creator.Fitness)


def init_selection():
    """  Choose a randomly sized subset of articles """
    # the_keys = ALL_FILES_KEYS  # no real need for a copy each time
    # np.random.shuffle(the_keys)
    # first, find the highest quality articles
    # then, the highest importance articles
    # then seed the individuals with random selections from these sets
    # then seed from individuals not in the individual yet
    hi_q_keys = np.random.permutation(ALL_FILES_HI_Q_KEYS)
    hi_i_keys = np.random.permutation(ALL_FILES_HI_I_KEYS)
    the_keys = np.random.permutation(ALL_FILES_KEYS)  # faster than shuffle
    final_idx = random.randint(config.min_count, len(the_keys))
    hi_q_entries = int(len(hi_q_keys) if final_idx * QUAL_RATIO > len(hi_q_keys) else final_idx * QUAL_RATIO)
    hi_i_entries = int(len(hi_i_keys) if final_idx * IMPT_RATIO > len(hi_i_keys) else final_idx * IMPT_RATIO)

    output = list(hi_q_keys[:hi_q_entries])
    output += list(hi_i_keys[:hi_i_entries])
    output += list(the_keys[:(final_idx - len(output))])
    output_set = list(set(output))  # fast deduping, plus more shuffling
    output = list(np.random.permutation(output_set))

    # need minimum quality/importance to even start caring
    # quality = sum(ALL_FILES[entry][QUALITY_INDEX] for entry in output)/float(final_idx)
    # importance = sum(ALL_FILES[entry][IMPORTANCE_INDEX] for entry in output)/float(final_idx)

    del the_keys  # attempt at memory handling
    del hi_q_keys
    del hi_i_keys
    del output_set
    # print("{} and {}".format(quality, importance))
    # ('random selection: {} len: {}'.format(output, len(output)))
    # print('Made an individual for the population')
    return output

toolbox = base.Toolbox()
toolbox.register('init_selection', init_selection)
toolbox.register("articles", tools.initCycle, creator.ArticleSet,
                 (toolbox.init_selection,), n=1)  # makes the initial list inside a tuple
toolbox.register("population", tools.initRepeat, list, toolbox.articles)


def evaluate_articles(individual, target_size, final_output=False):
    """Evaluates the fitness and return the error on the price and the time
    taken by the order if the chef can cook everything in parallel."""

    # go through and don't count the dupes
    individual = individual[0]  # because it's been tupled
    # print(individual)
    indiv_set = set(individual)
    set_size = float(len(indiv_set))
    if set_size:
        page_links = sum(ALL_FILES[entry][PAGE_LINKS_INDEX] for entry in indiv_set)/ALL_FILES_SIZE
        lang_links = sum(ALL_FILES[entry][LANG_LINKS_INDEX] for entry in indiv_set)/ALL_FILES_SIZE
        page_views = sum(ALL_FILES[entry][PAGE_VIEWS_INDEX] for entry in indiv_set)/ALL_FILES_SIZE
        page_size = sum(ALL_FILES[entry][PAGE_SIZE_INDEX] for entry in indiv_set)  # can change this to just a total
        quality = sum(ALL_FILES[entry][QUALITY_INDEX] for entry in indiv_set)/set_size
        importance = sum(ALL_FILES[entry][IMPORTANCE_INDEX] for entry in indiv_set)/set_size
    else:
        return 1000000000000000, 0, 0, 0, 0, 0  # ludicrous individual that should be dropped
    del indiv_set  # attempt at memory management
    return abs(page_size - target_size), (2.0 * page_links + 2.0 * lang_links + page_views)/5.0, 0, 0, quality, importance


def cxCounter(ind1, ind2, indpb):
    """Swaps the number of particular items between two individuals.
    Note that the individuals have decorations at this point, so it's not
    feasible to simple swap numbers"""
    if random.random() > indpb:
        # first, choose a length that is lower than either indiv's length
        if len(ind1[0]) and len(ind2[0]):
            swap_len = random.randint(0, min(len(ind1[0]), len(ind2[0]))-1)
            # now choose a start spot for each array
            start1 = random.randint(0, len(ind1[0]) - swap_len - 1)
            start2 = random.randint(0, len(ind2[0]) - swap_len - 1)
            tmp = ind1[0][start1:swap_len+start1]
            ind1[0][start1:len(tmp)+start1] = ind2[0][start2:swap_len+start2]
            ind2[0][start2:swap_len+start2] = tmp
            del tmp  # attempt at memory management
        return ind1, ind2
    else:
        return ind1, ind2


def mutCounter(individual):
    """Adds or remove an item from an individual"""
    # individual = individual[0]
    try:
        if random.random() > 0.5:
            the_keys = ALL_FILES_KEYSET
            indiv_set = set(individual[0])
            missing = list(the_keys - indiv_set)
            individual[0] = list(indiv_set)
            indiv_idx = random.randint(0,len(individual[0])-1)
            missing_idx = random.randint(0,len(missing)-1)
            if len(missing) and len(individual[0]):
                individual[0][indiv_idx] = missing[missing_idx]
            del indiv_set  # attempt at memory handling
            del missing
        else:
            # numpy.delete(individual[0], random.randint(0,len(individual) - 1))
            individual[0].remove(individual[0][random.randint(0,len(individual) - 1)])
            # use this as a chance to shrink a candidate
            #  = np.random.permutation(individual[0])  # faster than shuffle
            # final_idx = random.randint(0, len(the_keys))
            # individual[0] = the_keys[:final_idx].tolist()
            # del the_keys  # attempt at memory handling
        return individual,
    except:
        return individual,  # no mutation for you, buddy


toolbox.register("evaluate", evaluate_articles, target_size=config.target_size)
toolbox.register("mate", cxCounter, indpb=0.5)
toolbox.register("mutate", mutCounter)
toolbox.register("select", tools.selNSGA2)

toolbox.register("map", futures.map)  # to make things multicore


def get_page_val(page_id, idx):
    try:
        if idx == PAGE_TITLE_INDEX:
            return ALL_FILES[page_id][idx].encode('utf-8', errors='replace')
        elif idx == PAGE_SIZE_INDEX:
            return ALL_FILES[page_id][idx]
        else:
            return int((ALL_FILES[page_id][idx] * ranges[idx]) + min_array[idx])  # back to the original values
    except:
        # print ("Broken on Page ID {} for index {}".format(page_id, idx))
        return None

# -------------------------
# output functions
# -------------------------
def write_lines_by_key(key, n, hof, of):
    if key != 1:
        sorted_hof = sorted(hof, key=itemgetter(key), reverse=True)
    else:
        sorted_hof = hof
    if key == PAGE_SIZE_INDEX - 1:
        of.write("Top {} article sets by page size:\n\n".format(n))
    if key == PAGE_LINKS_INDEX - 1:
        of.write("Top {} article sets by popularity:\n\n".format(n))
        # of.write("Top {} article sets by page links:\n\n".format(n))
    if key == LANG_LINKS_INDEX - 1:
        of.write("Top {} article sets by language links:\n\n".format(n))
    if key == PAGE_VIEWS_INDEX - 1:
        of.write("Top {} article sets by page views:\n\n".format(n))
    if key == QUALITY_INDEX - 1:
        of.write("Top {} article sets by quality:\n\n".format(n))
    if key == IMPORTANCE_INDEX - 1:
        of.write("Top {} article sets by importance:\n\n".format(n))
    for count in range(n):
        indiv = sorted_hof[count]
        of.write("Rank: {}\tArticle count: {}\tSize diff: {}\tpage_links: {}\tlang_links: {}\tpage views: {}\tquality: {}\timportance: {}\nArticles:\n".format(
            count + 1, len(indiv[0]), indiv[1], indiv[2], indiv[3], indiv[4], indiv[5], indiv[6]))
        of.write("Title\tID\tPage Links\tLang Links\tPage Views\tPage Size\tMax Qual\tMax Impt\n")
        for page_id in indiv[0]:
            of.write("{title}\t{id}\t{plinks}\t{llinks}\t{pviews}\t{psize}\t{max_qual}\t{max_impt}\n".format(title=get_page_val(page_id, PAGE_TITLE_INDEX),
                                                                                                             id=page_id,
                                                                                                             plinks=get_page_val(page_id, PAGE_LINKS_INDEX),
                                                                                                             llinks=get_page_val(page_id, LANG_LINKS_INDEX),
                                                                                                             pviews=get_page_val(page_id, PAGE_VIEWS_INDEX),
                                                                                                             psize=get_page_val(page_id, PAGE_SIZE_INDEX),
                                                                                                             max_impt=get_page_val(page_id, IMPORTANCE_INDEX),
                                                                                                             max_qual=get_page_val(page_id, QUALITY_INDEX)))
        of.write("\n\n")


def print_top_n(hall_of_fame, n, file_name):
    with open(file_name, 'w') as of:
        real_n = n
        if n >= len(hall_of_fame) - 1:
            real_n = len(hall_of_fame) - 1
        # for count in range(1, 7):
        #    write_lines_by_key(count, real_n, hall_of_fame, of)
        #    of.write("\n\n")
        sorted_hof = sorted(hall_of_fame, key=itemgetter(1), reverse=False)
        write_lines_by_key(1, real_n, sorted_hof, of)
        # now, select the subset of the sorted hof that is up to 0.1 delta from the target size
        # that's the list to consider now
        sorted_len = 0
        for idx, entry in enumerate(sorted_hof):
            if entry[1] > config.target_size * 0.02:
                sorted_len = idx
                break
        print("Considering {} individuals for non-page size metrics out of {}".format(sorted_len, len(sorted_hof)))
        subset_hof = sorted_hof[0:sorted_len]
        write_lines_by_key(2, real_n, subset_hof, of)
        write_lines_by_key(5, real_n, subset_hof, of)
        write_lines_by_key(6, real_n, subset_hof, of)
        # now, look for the max quality and max importance collections
        # within 1% of the max size


def dedupe_hof(hof):
    article_set = set()
    name_list = []
    for indiv in hof:
        names = tuple(set(indiv[0]))
        if names not in article_set:
            article_set.add(names)
            name_list += [indiv]
        else:
            del indiv  # more memory management
    return name_list


def main():
    if config.testing:
        NGEN = 40
    else:
        NGEN = config.number_of_generations
    MU = 100
    LAMBDA = 200
    CXPB = 0.3
    MUTPB = 0.6

    pop = toolbox.population(n=MU)
    hof = tools.ParetoFront()

    size_stats = tools.Statistics(key=lambda ind: ind.fitness.values[0])
    page_link_stats = tools.Statistics(key=lambda ind: ind.fitness.values[1])
    # lang_link_stats = tools.Statistics(key=lambda ind: ind.fitness.values[2])
    # page_view_stats = tools.Statistics(key=lambda ind: ind.fitness.values[3])
    quality_stats = tools.Statistics(key=lambda ind: ind.fitness.values[4])
    importance_stats = tools.Statistics(key=lambda ind: ind.fitness.values[5])
    stats = tools.MultiStatistics(size=size_stats,
                                  page_links=page_link_stats,
                                  # lang_links=lang_link_stats,
                                  # page_views=page_view_stats,
                                  quality=quality_stats,
                                  importance=importance_stats)
    stats.register("avg", numpy.mean, axis=0)
    stats.register("std", numpy.std, axis=0)
    stats.register("min", numpy.min, axis=0)

    algorithms.eaMuPlusLambda(pop, toolbox, MU, LAMBDA, CXPB, MUTPB, NGEN,
                              stats, halloffame=hof)

    return pop, stats, hof


if __name__ == "__main__":
    trial_string = "Trial-" + time.ctime().replace(' ', '-').replace(':', '-')
    pop, stats, hof = main()
    del pop
    del stats
    print("\n And Now, for the hall of fame:")
    deduped_hof = dedupe_hof(hof)
    to_print_hof = []
    count = 0
    for article_set in deduped_hof:
        scores = evaluate_articles(article_set, config.target_size, final_output=True)
        to_print_hof += [((tuple(set(article_set[0])),
                           scores[0], scores[1], scores[2],
                           scores[3], scores[4], scores[5]))]
        # tuple where first entry is the article list, then the score tuple is the second entry
        # has the 'none' to align the indeces with the original scoring in the 'all' files
    print_top_n(to_print_hof, config.max_num_candidate_sets, trial_string + ".txt")
    # open(trial_string + ".pkl", 'wb') as hof_file:  # no point, unicode errors prevent reading it back in
    #    pickle.dump(deduped_hof, hof_file)  # should dedupe, but Windows is being nastily aggressive
