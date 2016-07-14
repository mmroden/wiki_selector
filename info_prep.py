import lzma
import re
import os
import config
import operator


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
IMPORTANCE_RANKS = {"Top-Class": 1,
                    "High-Class": 0,
                    "Mid-Class": -1,
                    "Low-Class": -1}

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


def read_file(file_name, encoding='utf-8', page_id_index=0, all_file=False):
    """This function will read in a file and put it into a hash for fast access"""
    with lzma.open(file_name) as page_file:
        lines = page_file.read().decode(encoding, errors='replace')

    print("Imported file {}, parsing".format(file_name))
    parsed_lines = {}
    count = 0
    for line in split_iter(lines):
        tup = tuple(number_conv(entry) for entry in line.split('\t'))
        # restore these next three lines if you think there can be id collisions
        # if tup[page_id_index] not in parsed_lines:
        #    parsed_lines[tup[page_id_index]] = []
        # parsed_lines[tup[page_id_index]] += [tup]
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
        if config.testing:
            count += 1
            if count > config.testing_size:  # a subset of articles
               break
    print("File {} is parsed, precull count is {}".format(file_name, len(parsed_lines)))
    if all_file:
        culled_lines = cull_lines(parsed_lines, page_id_index)
        print("Lines have been culled, current cull count is {}".format(len(culled_lines)))
        del parsed_lines  # memory management attempt
        return culled_lines
    else:
        return parsed_lines


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