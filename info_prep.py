import lzma
import re
import os
import config
import operator
import math


QUALITY_RANKS = {"FA-Class": 2,
                 "FL-Class": 1,
                 "A-Class": 0,
                 "GA-Class": -1,
                 "B-Class": -1,
                 "C-Class": -1,
                 "Start-Class": -2,
                 "Stub-Class": -3,
                 "List-Class": -4,
                 "Assessed-Class": -5}  # arbitrary class weights
QUALITY_SCORES = {"FA-Class": 500,
                  "FL-Class": 500,
                  "A-Class": 400,
                  "GA-Class": 400,
                  "B-Class": 300,
                  "C-Class": 225,
                  "Start-Class": 150,
                  "All-Others": 0}  # following Martin's metrics

IMPORTANCE_RANKS = {"Top-Class": 1,
                    "High-Class": 0,
                    "Mid-Class": -1,
                    "Low-Class": -1}

IMPORTANCE_SCORES = {"Top-Class": 400,
                     "High-Class": 300,
                      "Mid-Class": 200,
                    " Low-Class": 100}


BLANK_QUALITY = 0
BLANK_IMPT = 0  # we just don't know, assume it's viable

# goddamn this is horrible spaghetti code
# I just want to get these values out for reasonable printouts
start_index = 2
end_index = 8  # to be inclusive in the last index, which is quality
impt_index = end_index - 1
qual_index = end_index - 2
page_size_index = start_index
max_array = [0 for x in range(0, end_index)]
min_array = [100000000000000 for x in range(0, end_index)]
ranges = [0 for x in range(0, end_index)]

def split_iter(string):
    ''' from http://stackoverflow.com/questions/3862010/is-there-a-generator-version-of-string-split-in-python'''
    return (x.group(0)[:-1] for x in re.finditer(r'(.*\n|.+$)', string))


def number_conv(entry):
    """
    Sanitizes inputs to integers and floats, since those are smaller and better handled by math
    :param entry:
    :return:
    """
    try:
        return int(entry)
    except:
        try:
            return float(entry)
        except:
            return entry


def get_quality_and_importance(rating):
    try:
        classes = rating.split('=')[1]
        qual, impt = classes.split(':')
        if qual in QUALITY_RANKS:
            qual_num = QUALITY_RANKS[qual]
        else:
            qual_num = None
        if impt in IMPORTANCE_RANKS:
            impt_num = IMPORTANCE_RANKS[impt]
        else:
            impt_num = None
        return qual_num, impt_num
    except:
        return None, None # don't return anything, don't count it


def normalize_value(idx, x, mins, ranges):
    if idx > 2:  # don't normalize on size, id, or title
        return (x - mins[idx])/ranges[idx]
    return x


def cull_lines(parsed_lines, page_id_index):
    """
    This will take the top N% of each entry in a row, where N is a configuration variable
    To do so:
        sort the rows by each column
        take the top N% of the rows
        find the min and max of each row in sequence
        then renormalize each row entry
    written for the 'all_lines' collection created in read_file
    :param parsed_lines:  the lines from the all_lines file (page name, page id, stats)
    :param page_id_index: the index of the page id
    :return:
    """
    parsed_values = list(parsed_lines.values())  # dictionary isn't helpful here
    culled_lines = {}
    prenorm_lines = {}  # lines before normalization
    for idx in range(start_index, end_index):
        sorted_list = sorted(parsed_values, key=lambda x: x[idx], reverse=True)
        max_array[idx] = sorted_list[0][idx]
        min_array[idx] = sorted_list[len(sorted_list)-1][idx]
        ranges[idx] = float(max_array[idx] - min_array[idx])
        if idx == impt_index:
            for tup in sorted_list:
                if tup[idx] >= IMPORTANCE_RANKS['Top-Class']:
                    if tup[page_id_index] not in prenorm_lines:
                        prenorm_lines[tup[page_id_index]] = tup
        if idx == qual_index:
            for tup in sorted_list:
                if tup[idx] >= QUALITY_RANKS['FL-Class']:
                    if tup[page_id_index] not in prenorm_lines:
                        prenorm_lines[tup[page_id_index]] = tup
        # make sure that the qual/impt stuff is all there, then add more to the cull percentage
        if idx != page_size_index:  # except for pages that are just big.  We don't care about those
            for i, tup in enumerate(sorted_list):
                if i > len(sorted_list) * config.cull_percentage:
                    break
                else:
                    if tup[page_id_index] not in prenorm_lines:
                        prenorm_lines[tup[page_id_index]] = tup
    # now, normalize by the min/max
    print("Value ranges: ")
    print(max_array, min_array, ranges)
    for line in list(prenorm_lines.values()):
        normalized_line = tuple(normalize_value(idx, x, min_array, ranges) for idx, x in enumerate(line))
        culled_lines[normalized_line[page_id_index]] = normalized_line
    del prenorm_lines
    del parsed_values  # attempts at memory management
    return culled_lines


def read_file(file_name, encoding='utf-8', page_id_index=0, all_file=False, remove_excluded=True):
    """
    This function will read in a file and put it into a hash for fast access
    A lot of the 'all_file" functionality is cruft at this point
    """
    with lzma.open(file_name) as page_file:
        lines = page_file.read().decode(encoding, errors='replace')

    print("Imported file {}, parsing".format(file_name))
    parsed_lines = {}
    count = 0
    excluded_set = set(config.excluded_projects)
    for line in split_iter(lines):
        tup = tuple(number_conv(entry) for entry in line.split('\t'))
        # restore these next three lines if you think there can be id collisions
        # if tup[page_id_index] not in parsed_lines:
        #    parsed_lines[tup[page_id_index]] = []
        # parsed_lines[tup[page_id_index]] += [tup]
        # remove any mention of an excluded project
        exclude_entry = False
        for entry in tup[6:]:
            project_name = entry.split('=')[0]
            if project_name in excluded_set:
                exclude_entry = True
        if not exclude_entry:
            if all_file:  # that is, the line is of variable length, because it is from the 'all' file
                ratings = tup[6:]
                # if config.testing:
                #    print(ratings)
                qual_ranking = impt_ranking = impt_total = qual_total = 0
                max_qual = 0
                max_impt = 0
                for rating in ratings:
                    qual, impt = get_quality_and_importance(rating)
                    if qual is not None:
                        if qual > max_qual:
                            max_qual = qual
                    if impt is not None:
                        if impt > max_impt:
                            max_impt = impt
                real_tup = tuple(tup[:6] + (max_qual, max_impt))
                if max_qual >= 0 or max_impt >= 0:  # disregard articles we know are low quality/unimportant
                    parsed_lines[real_tup[page_id_index]] = real_tup
            else:
                parsed_lines[tup[page_id_index]] = tup
#        if config.testing:
#            count += 1
#            if count > config.testing_size:  # a subset of articles
#               break
    print("File {} is parsed, precull count is {}".format(file_name, len(parsed_lines)))
    if all_file:
        culled_lines = cull_lines(parsed_lines, page_id_index)
        print("Lines have been culled, current cull count is {}".format(len(culled_lines)))
        del parsed_lines  # memory management attempt
        return culled_lines
    else:
        return parsed_lines


def calculate_article_score(article, project_name):
    """
    using the formula laid out by Martin et al for importance:
    Q + I = Q + IA + IScope + 50 (log_10 page views) + 100 * (log_10 page links) + 250 (log_10 lang links)
    if the project has no quality, then 4/3 * (page views, page links, lang links) using the last three terms above
    If the project_name is not given (ie, is None), then this scoring mechanism
    will return the highest score period.
    :param project_name:
    :param article:
    :return:
    """
    try:
        page_view_metric = 50 * math.log10(article[5])
    except:
        page_view_metric = 0
    try:
        page_link_metric = 100 * math.log10(article[3])
    except:
        page_link_metric = 0
    try:
        lang_link_metric = 250 * math.log10(article[4])
    except:
        lang_link_metric = 0
    # gotta get the max importance and quality rating
    highest_quality = 0
    highest_importance = 0
    for entry in article[6:]:
        first_split = entry.split('=')
        project = first_split[0]
        if project == project_name or not project_name:
            second_split = first_split[1].split(':')
            quality = second_split[0]
            importance = second_split[1]
            try:
                quality_score = QUALITY_SCORES[quality]
            except:
                quality_score = QUALITY_SCORES['All-Others']
            if quality_score > highest_quality:
                highest_quality = quality_score
            try:
                importance_score = IMPORTANCE_SCORES[importance]
            except:
                importance_score = 0  # zero means multiplying external quality by 4/3
            if importance_score > highest_importance:
                highest_importance = importance_score
    if highest_importance:
        return highest_importance + highest_quality + page_view_metric + page_link_metric + lang_link_metric
    else:
        return highest_quality + 4.0/float(3.0) * (page_view_metric + page_link_metric + lang_link_metric)


def print_collection(article_id_set, all_articles, filename):
    """
    Given a list of article ids and the articles themselves, print everything out into
    the specified file name
    :param article_id_list:
    :return:
    """
    with open(filename, "w") as of:
        of.write("Article Name\tArticle ID\tPage Size\tPage Links\tLang Links\tPage Views\n")
        for article in article_id_set:
            for idx in list(range(6)):
                try:
                    of.write("{}\t".format(all_articles[article][idx]))
                except:
                    of.write("None\t")
            of.write("\n")


def decompress_chunk(decompressor, data, encoding, default_max=1000000000):
    links = None
    curr_max = default_max
    while not links and curr_max > 0:
        try:
            links = decompressor.decompress(data=data,
                                            max_length=curr_max).decode(encoding, errors='replace')
        except:
            curr_max -= 100
    if links:
        return links
    else:
        return None


def prepare_seeded_set(seed_set, all_articles, encoding='utf-8'):

    page_file_name = os.path.join(config.which_wiki, 'pages.lzma')
    link_file_name = os.path.join(config.which_wiki, 'pagelinks.lzma')

    # first, get the title to id translation
    title_to_id = {}
    for article_tup in all_articles.values():
        title_to_id[article_tup[0]] = int(article_tup[1])

    print ("Title to ID mapper read in.  Length: {}".format(len(title_to_id)))
    
    # first, we go through the links, and build up a set of titles that they are linked to
    # then, we go through the page set and find the ids for those titles.
    # if the seed set size + the linked size is contained in the target size, expand the
    # seed set and repeat
    title_map = {}
    max_chunk_size = 1000000000
    decompressor = lzma.LZMADecompressor()
    with open(link_file_name, 'rb') as link_file:
        data = link_file.read()
        # now, decompress a chunk at a time
        # if the line doesn't end in a carriage return, keep that last bit for the next line
        links = decompress_chunk(decompressor, data, encoding, max_chunk_size)
        count = 1
        while not decompressor.needs_input:
            print("reading decompressed lines {}".format(count))
            count += 1
            if config.testing and count > 2:
                break
            for link_line in links:  # do I need to worry about incomplete lines?
                tup = tuple(entry for entry in link_line.split('\t'))
                id_from_title = None
                try:
                    id_from_title = int(title_to_id[tup[1]])
                except:
                    pass  # broken somehow
                if id_from_title:  # two try/excepts in case id_from_title is busted
                    try:
                        title_map[tup[0]] += [id_from_title]
                    except:
                        title_map[tup[0]] = [id_from_title]
            links = decompress_chunk(decompressor, decompressor.unused_data, encoding, max_chunk_size)
    print ("Link Files have been imported. Length of links: {}".format(len(title_map)))
    expanded_id_set = set()

    print("Expanded set created now.")
    # now, do a size check
    print("Given Article Set Size: {}".format(len(seed_set)))
    print("Expanded Article Set Size: {}".format(len(expanded_id_set)))
    expanded_id_list = list(expanded_id_set)
    total_size = 0
    for id in expanded_id_list:
        total_size += all_articles[id][2]
    for id in seed_set:
        total_size += all_articles[id][2]

    print("New size: {}".format(total_size))
    if total_size < config.target_size:
        print("Total size is less than the target size, expanding for all new articles and then rerunning.")
    else:
        print("Total size exceeds target size, beginning selection process.")



def get_seed_articles():
    """
    Reads the configured all.lzma file to get the top N ranked articles for all projects in the configured
    Emphasized Projects list.
    Returns the seed set as well as a set of articles filtered for excluded wikiprojects
    :return:
    """
    all_articles = read_file(os.path.join(config.which_wiki, 'all.lzma'), page_id_index=1, all_file=False)  # we want preprocessed content

    project_set = set(config.emphasized_projects)
    considered_articles = {project: [] for project in project_set}

    # first, now that we've read everything in, get only articles associated with the given project list
    key_list = list(all_articles.keys())
    for key in key_list:
        article = all_articles[key]
        all_projects = set(entry.split('=')[0] for entry in article[6:])
        for project in all_projects:
            if project in project_set:
                considered_articles[project] += [(article[1], calculate_article_score(article, project))]

    article_subset = {project: [] for project in project_set}

    # now get the sorted and truncated list of entries by project
    # also have to do a size check; error out now if we're already over the size restriction
    total_size = 0
    seed_article_set = set()
    for project in project_set:
        sorted_subset = sorted(considered_articles[project],
                               key=lambda x: x[1],
                               reverse=True)[0:config.min_number_emphasized_articles]
        article_subset[project] = tuple(entry[0] for entry in sorted_subset)
        for entry in article_subset[project]:
            seed_article_set.add(entry)

    for article_id in seed_article_set:
        total_size += all_articles[article_id][2]

    if total_size > config.target_size:
        print("Seed size is bigger than target size; please lower the number of projects or articles per project.")
        print("Seed size: {}  Target size: {}".format(total_size, config.target_size))
        assert False

    # now, filter each set of considered articles
    return seed_article_set, all_articles


def print_list_sorted_by_metric():
    all_articles = read_file(os.path.join(config.which_wiki, 'all.lzma'), page_id_index=1,
                             all_file=False)  # we want preprocessed content
    article_list_by_score = [(article, calculate_article_score(article, None)) for article in list(all_articles.values())]
    sorted_article_list = sorted(article_list_by_score, key=lambda x: x[1], reverse=True)
    total_size = 0
    max_idx = 0
    article_id_set = set()
    for idx, article in enumerate(sorted_article_list):
        total_size += article[0][2]  # look up the article by id, then get the second element for size
        if total_size > config.target_size:
            max_idx = idx
            break
        else:
            article_id_set.add(article[0][1])

    list_name = "Sorted_List_{}.txt".format(config.which_wiki)
    print_collection(article_id_set, all_articles, list_name)


def check_sanity(all_files):
    '''
    This function will make sure that the original pages are present in the 'all_pages' collections
    :param all_files:
    :return:
    '''
    page_files = read_file(os.path.join(config.which_wiki, 'pages.lzma'), page_id_index=0)
    count = 0
    main_count = 0
    for k, v in page_files.items():
        count += 1
        if not int(v[-1]):
            # the last entry of the pages file is whether or not this page is a redirect;
            # we ignore redirects
            if k in all_files:
                main_count += 1
    print("All pages: {}, page non-redirect count: {}".format(len(all_files),
                                                              main_count))
    assert (main_count - len(all_files) < config.acceptable_epsilon)


def prep_files():
    '''
    first, just read in all the files, and link things up via page_ids
    From the README:
        pageviews: page_title view_count
        pages: page_id page_title page_size is_redirect
        pagelinks: source_page_id target_page_title
        langlinks: source_page_id language_code target_page_title
        redirects: source_page_id target_page_title
        ratings: page_title project quality importance
        all: page_title page_id page_size pagelinks_count langlinks_count pageviews_count [rating1] [rating2] ...

    All that's returned from this is the 'all' collection, indexed by page_id
    :return: hashes by page_ids
    '''
    all_files = read_file(os.path.join(config.which_wiki, 'all.lzma'),
                          page_id_index=1, all_file=True)
    # check_sanity(all_files)  # only check sanity when not doing parallel execution; otherwisee
    # you will run out of memory on a system with less than ~4gb per core
    return all_files


def main():
    prep_files()


if __name__ == "__main__":
    main()
