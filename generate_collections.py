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

ALL_FILES = prep_files()
PAGE_LINKS_INDEX = 3
LANG_LINKS_INDEX = 4
PAGE_VIEWS_INDEX = 5
PAGE_SIZE_INDEX = 2

creator.create("Fitness", base.Fitness, weights=(-1.0, 1.0, 1.0, 1.0))
creator.create("Individual", Counter, fitness=creator.Fitness)

toolbox = base.Toolbox()
toolbox.register("attr_item", random.choice, ITEMS_NAME)
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_item, IND_INIT_SIZE)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)


def init_selection():
    """  Choose a randomly sized subset of articles """
    the_keys = random.shuffle(list(ALL_FILES.keys()))
    return the_keys[:random.randint(10, len(the_keys))]


def evaluate_articles(individual, target_size):
    """Evaluates the fitness and return the error on the price and the time
    taken by the order if the chef can cook everything in parallel."""

    # go through and don't count the dupes
    indiv_set = set(individual)
    page_links = sum(ALL_FILES[entry][PAGE_LINKS_INDEX] for entry in indiv_set)
    lang_links = sum(ALL_FILES[entry][LANG_LINKS_INDEX] for entry in indiv_set)
    page_views = sum(ALL_FILES[entry][PAGE_VIEWS_INDEX] for entry in indiv_set)
    page_size = sum(ALL_FILES[entry][PAGE_SIZE_INDEX] for entry in indiv_set)  # can change this to just a total
    return abs(page_size - target_size), page_links, lang_links, page_views


def cxCounter(ind1, ind2, indpb):
    """Swaps the number of particular items between two individuals"""
    if random.random() > indpb:
        randint1 = random.randint(0, len(ind1))
        randint2 = random.randint(0, len(ind2))
        # removing dupes with the list/set transformation
        new_ind1 = list(set(ind1[0:randint1] + ind2[randint2:len(ind2)]))
        new_ind2 = list(set(ind2[0:randint2] + ind1[randint1:len(ind1)]))
        return new_ind1, new_ind2
    else:
        return ind1, ind2


def mutCounter(individual):
    """Adds or remove an item from an individual"""
    if random.random() > 0.5:
        the_keys = list(ALL_FILES.keys())
        
    else:
        individual.remove(individual[random.randint(0,len(individual))])
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

    price_stats = tools.Statistics(key=lambda ind: ind.fitness.values[0])
    time_stats = tools.Statistics(key=lambda ind: ind.fitness.values[1])
    stats = tools.MultiStatistics(price=price_stats, time=time_stats)
    stats.register("avg", numpy.mean, axis=0)
    stats.register("std", numpy.std, axis=0)
    stats.register("min", numpy.min, axis=0)

    algorithms.eaMuPlusLambda(pop, toolbox, MU, LAMBDA, CXPB, MUTPB, NGEN,
                              stats, halloffame=hof)

    return pop, stats, hof


if __name__ == "__main__":
    _, _, hof = main()
