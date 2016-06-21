import lzma
import re
import os
import config


QUALITY_RANKS = {"FA-Class": 6,
                 "FL-Class": 5,
                 "A-Class": 4,
                 "GA-Class": 3,
                 "B-Class": 2,
                 "C-Class": 1,
                 "Start-Class": 0,
                 "Stub-Class": -1,
                 "List-Class": -2,
                 "Assessed-Class": -3}  # arbitrary class weights
IMPORTANCE_RANKS = {"Top-Class": 3,
                    "High-Class": 2,
                    "Mid-Class": 1,
                    "Low-Class": 0}

BLANK_QUALITY = -2.0
BLANK_IMPT = -2.0


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
        qual_num = impt_num = 0
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


def read_file(file_name, encoding='utf-8', page_id_index=0, all_file=False):
    """This function will read in a file and put it into a hash for fast access"""
    with lzma.open(file_name) as page_file:
        lines = page_file.read().decode(encoding)

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
                    qual_ranking += qual
                    qual_total += 1
                    if qual > max_qual:
                        max_qual = qual
                if impt is not None:
                    impt_ranking += impt
                    impt_total += 1
                    if impt > max_impt:
                        max_impt = impt
            if qual_total:
                qual_ranking /= float(qual_total)
            if impt_total:
                impt_ranking /= float(impt_total)
            if qual_total and impt_total:
                real_tup = tuple(tup[:6] + (max_qual, max_impt))  #(qual_ranking, impt_ranking))
                # if config.testing:
                #    print(qual_ranking, impt_ranking)
                #    try:
                #        print(real_tup)
                #    except:
                #        print("tup breaks character encodings")
                if max_qual > 0 and max_impt > 0:
                    # if config.testing:
                    #    try:
                    #        print(real_tup)
                    #        print(qual_total, impt_total)
                    #    except:
                    #        print("tup breaks character encodings")
                    parsed_lines[real_tup[page_id_index]] = real_tup
            else:
                pass  # do nothing, the article is not worth including
                # parsed_lines[tup[page_id_index]] = tuple(tup[:6] + (BLANK_QUALITY, BLANK_IMPT))
        else:
            parsed_lines[tup[page_id_index]] = tup
        if config.testing:
            count += 1
            if count > config.testing_size:  # a subset of articles
               break
    print("File {} is parsed, final count is {}".format(file_name, len(parsed_lines)))
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