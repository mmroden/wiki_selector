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
    page_files = read_file(os.path.join(config.which_wiki, 'pages.lzma', page_id_index=0))
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


class LankLink:
    '''
    A class that will store the language links
    '''
    def __init__(self, source_page_id, language_code, target_page_title):
        self.language_code = language_code
        self.target_page_title = target_page_title
        self.source_page_id = source_page_id


class WikiRating:
    '''
    A class that holds the ratings for a page via project
    '''
    def __init__(self, page_title, project, quality, importance):
        self.page_title = page_title
        self.project = project
        self.quality = quality
        self.importance = importance


class WikiProjects:
    '''
    A class for projects
    '''
    def __init__(self, file_name='ratings.xz', encoding='utf-8'):
        with lzma.open(file_name) as ratings_file:
            ratings = ratings_file.read().decode(encoding)

        ratings_lines = ratings.split('\n')
        self.projects = {}
        for line in ratings_lines:
            tup = tuple(line.split('\t'))
            if len(tup) == 4:
                try:
                    self.projects[tup[1]] += [tup]
                except:
                    self.projects[tup[1]] = [tup]


class WikiPages:
    '''
    A class for pages
    '''
    def __init__(self, page_file_name='pages.xz', encoding='utf-8',
                 link_file_name='page_links.xz',
                 lang_link_file_name='lang_links.xz',
                 redirect_file_name='redirects.xz'):
        """

print(broken_count)
        """
        pass


class WikiPage:
    def __init__(self, page_title, is_redirect):
        self.page_title = page_title
        self.view_count = None  # not yet set
        self.link_target_page_titles = None  # should be a tuple
        self.langlinks = None  # should be a tuple of LankLinks
        self.redirects = None  # purely titles
        self.ratings = None  # a tuple of ratings



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
    all_files = read_file(os.path.join(config.which_wiki, 'all.lzma', page_id_index=1))
    check_sanity(all_files)


def main():
    prep_files()


if __name__ == "__main__":
    main()