import lzma


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
        with lzma.open(page_file_name) as page_file:
            pages = page_file.read().decode(encoding)
        page_lines = pages.split('\n')
        self.pages = {}
        for line in page_lines:
            tup = tuple(line.split('\t'))
            assert(tup[0] not in self.pages)
            self.pages[tup[0]] = tup


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
        pages: page_id page_title is_redirect
        pagelinks: source_page_id target_page_title
        langlinks: source_page_id language_code target_page_title
        redirects: source_page_id target_page_title
        ratings: page_title project quality importance

    The resulting object will be a named tuple:
    pages[page_id] = ("page_title": page_title, "view_count":view_count,
    :return: hashes by page_ids
    '''

    return projects


def main():
    prep_files()


if __name__ == "__main__":
    main()