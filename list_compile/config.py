import os


metadata_location = os.environ.get('METADATA_LOCATION', 'http://download.kiwix.org/wp1/')
which_wiki = os.environ.get('WHICH_WIKI', 'enwiki_2017-07/')

acceptable_epsilon = os.environ.get('EPSILON', 20)  # allowed slippage between pages and all

max_num_candidate_sets = int(os.environ.get('MAX_NUM_SETS', 3))

testing = bool(int(os.environ.get('TESTING', 0)))
testing_size = int(os.environ.get('TESTING_SIZE', 10000))  # number of articles to consider for a test

if testing:
    target_size = testing_size * 10000  # shoot for 10000 byte articles
else:
    target_size = int(os.environ.get('SIZE', 10000000000))  # in bytes

cull_percentage = float(os.environ.get('CULL_PERCENTAGE', 0.005))
number_of_generations = int(os.environ.get('NUMBER_OF_GENERATIONS', 500))
min_count = int(os.environ.get("MIN_COUNT", 1000))  # smallest number of articles in any initial population

# we're going to seed all individuals with some emphasized projects
# that is, we're going to take the top N articles, as determined by a combination of
# lank links, page links, and page views, for the given projects,
# and ensure that those pages are present in the collection.
# all individuals created will have that set of articles, and the preservation of that set
# of articles will be a metric for success.
default_projects = ("Biography", "Wikipedia_vital", "History_of_science", "Medicine", "Marine_life",
                    "Philosophy", "Physics", "Biography_(science_and_academia)", "Film", "Aviation",
                    "National_Register_of_Historic_Places", "Military_history", "Paleontology",
                    "WikiProject_Cities", "Food_and_drink", "Ethics", "Computing", "Ships",
                    "Dinosaurs", "Amphibian_and_reptile", "History", "Mathematics")
emphasized_projects = os.environ.get('EMPHASIZED_PROJECTS', default_projects)
min_number_emphasized_articles = int(os.environ.get("MIN_EMPH", 20))

excluded_projects = ()  # "Chemistry", "Professional_wrestling", "Pornography")  # selected somewhat arbitrarily

'''
# as of August 2017, the ftp access for wiki metadata from kiwix is no longer online.
ftp_site = os.environ.get('FTP_SITE', 'wp1.kiwix.org')
ftp_user = os.environ.get('FTP_USER', 'wp1')
ftp_pass = os.environ.get('FTP_PASS')  # going to need to get one of these
ftp_port = int(os.environ.get('FTP_PORT', 20))

'''