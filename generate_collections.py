"""This example shows a possible answer to a problem that can be found in this
xkcd comics: http://xkcd.com/287/. In the comic, the characters want to get
exactly 15.05$ worth of appetizers, as fast as possible."""
import random
from operator import attrgetter
from collections import Counter
from info_prep import prep_files
import config

# We delete the reduction function of the Counter because it doesn't copy added
# attributes. Because we create a class that inherit from the Counter, the
# fitness attribute was not copied by the deepcopy.
del Counter.__reduce__

import numpy

from deap import algorithms
from deap import base
from deap import creator
from deap import tools


def create_dummy_data_fast():
    """
    for testing purposes and rapid iteration, make a structure similar to all_pages
    but just not as big.  Helps with debugging what happens after files are loaded
    """
    dummy_wiki_size = 1000
    dummy_wiki = {}
    for i in range(dummy_wiki_size):
        idx = i * 100
        dummy_wiki[idx] = (idx, "dummy{}".format(idx), random.randint(0,100),
                           random.randint(0,100), random.randint(0,100),
                           random.randint(0,100))
    return dummy_wiki

ALL_FILES = create_dummy_data_fast()  # prep_files()
ALL_FILES_KEYS = list(ALL_FILES.keys())
ALL_FILES_KEYSET = set(ALL_FILES_KEYS)
PAGE_LINKS_INDEX = 3
LANG_LINKS_INDEX = 4
PAGE_VIEWS_INDEX = 5
PAGE_SIZE_INDEX = 2


creator.create("Fitness", base.Fitness, weights=(-1.0, 1.0, 1.0, 1.0))
creator.create("ArticleSet", list, fitness=creator.Fitness)


def init_selection():
    """  Choose a randomly sized subset of articles """
    the_keys = ALL_FILES_KEYS.copy()
    random.shuffle(the_keys)
    output = the_keys[:random.randint(0, len(the_keys))]
    # print('initial selection: {}'.format(output))
    return output

toolbox = base.Toolbox()
toolbox.register('init_selection', init_selection)
toolbox.register("articles", tools.initCycle, creator.ArticleSet,
                 (toolbox.init_selection,), n=1)  # makes the initial list inside a tuple
toolbox.register("population", tools.initRepeat, list, toolbox.articles)


def evaluate_articles(individual, target_size):
    """Evaluates the fitness and return the error on the price and the time
    taken by the order if the chef can cook everything in parallel."""

    # go through and don't count the dupes
    individual = individual[0]  # because it's been tupled
    # print(individual)
    indiv_set = set(individual)
    page_links = sum(ALL_FILES[entry][PAGE_LINKS_INDEX] for entry in indiv_set)
    lang_links = sum(ALL_FILES[entry][LANG_LINKS_INDEX] for entry in indiv_set)
    page_views = sum(ALL_FILES[entry][PAGE_VIEWS_INDEX] for entry in indiv_set)
    page_size = sum(ALL_FILES[entry][PAGE_SIZE_INDEX] for entry in indiv_set)  # can change this to just a total
    return abs(page_size - target_size), page_links, lang_links, page_views


def cxCounter(ind1, ind2, indpb):
    """Swaps the number of particular items between two individuals.
    Note that the individuals have decorations at this point, so it's not
    feasible to simple swap numbers"""
    if random.random() > indpb:
        ind1 = ind1[0]
        ind2 = ind2[0]
        randint1 = random.randint(0, len(ind1))
        randint2 = random.randint(0, len(ind2))
        # removing dupes with the list/set transformation
        new_ind1 = list(set(ind1[0:randint1] + ind2[randint2:len(ind2)]))
        new_ind2 = list(set(ind2[0:randint2] + ind1[randint1:len(ind1)]))
        return new_ind1, new_ind2
        #return ind2, ind1
    else:
        return ind1, ind2


def mutCounter(individual):
    """Adds or remove an item from an individual"""
    # individual = individual[0]
    if random.random() > 0.5:
        the_keys = ALL_FILES_KEYSET.copy()
        indiv_set = set(individual[0])
        missing = list(the_keys - indiv_set)
        individual[0] = list(indiv_set)
        indiv_idx = random.randint(0,len(individual[0])-1)
        missing_idx = random.randint(0,len(missing)-1)
        try:
            if len(missing) and len(individual[0]):
                individual[0][indiv_idx] = missing[missing_idx]
        except:
            # debugging messages I'll leave in for now
            print("Missing: ", missing, "Individual: ", individual,
                  "M idx", missing_idx, "indiv_idx", indiv_idx,
                  len(missing), len(individual[0]))
            assert False
    else:
        individual[0].remove(individual[0][random.randint(0,len(individual))])
    return individual,


toolbox.register("evaluate", evaluate_articles, target_size=config.target_size)
toolbox.register("mate", cxCounter, indpb=0.5)
toolbox.register("mutate", mutCounter)
toolbox.register("select", tools.selNSGA2)


def main():
    NGEN = 40
    MU = 100
    LAMBDA = 200
    CXPB = 0.3
    MUTPB = 0.6

    pop = toolbox.population(n=MU)
    hof = tools.ParetoFront()

    size_stats = tools.Statistics(key=lambda ind: ind.fitness.values[0])
    page_link_stats = tools.Statistics(key=lambda ind: ind.fitness.values[1])
    lang_link_stats = tools.Statistics(key=lambda ind: ind.fitness.values[2])
    page_view_stats = tools.Statistics(key=lambda ind: ind.fitness.values[3])
    stats = tools.MultiStatistics(size=size_stats,
                                  page_links=page_link_stats,
                                  lang_links=lang_link_stats,
                                  page_views=page_view_stats)
    stats.register("avg", numpy.mean, axis=0)
    stats.register("std", numpy.std, axis=0)
    stats.register("min", numpy.min, axis=0)

    algorithms.eaMuPlusLambda(pop, toolbox, MU, LAMBDA, CXPB, MUTPB, NGEN,
                              stats, halloffame=hof)

    return pop, stats, hof


if __name__ == "__main__":
    _, _, hof = main()
    print("\n And Now, for the hall of fame:")
    for indiv in hof:
        print("\nIndividual stats: ", evaluate_articles(indiv, config.target_size))