import lzma
import re
import os
import config


def split_iter(string):
    ''' from http://stackoverflow.com/questions/3862010/is-there-a-generator-version-of-string-split-in-python'''
    return (x.group(0)[:-1] for x in re.finditer(r'(.*\n|.+$)', string))


def read_file(file_name, encoding='utf-8', page_id_index=0):
    with lzma.open(file_name) as page_file:
        lines = page_file.read().decode(encoding)

    print("Imported file {}, parsing".format(file_name))
    parsed_lines = {}
    for line in split_iter(lines):
        tup = tuple(line.split('\t'))
        if tup[page_id_index] not in parsed_lines:
            parsed_lines[tup[page_id_index]] = []
        parsed_lines[tup[page_id_index]] += [tup]

    return parsed_lines


def check_sanity(all_files):
    page_files = read_file(os.path.join(config.which_wiki, 'pages.lzma'), page_id_index=0)
    count = 0
    main_count = 0
    for k, v in page_files.items():
        count += 1
        if not int(v[0][-1]):
            if k in all_files:
                try:
                    main_count += 1
                except:
                    pass
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

    The resulting object will be a named tuple:
    pages[page_id] = ("page_title": page_title, "view_count":view_count,
    :return: hashes by page_ids
    '''
    all_files = read_file(os.path.join(config.which_wiki, 'all.lzma'), page_id_index=1)
    check_sanity(all_files)


def main():
    prep_files()


if __name__ == "__main__":
    main()