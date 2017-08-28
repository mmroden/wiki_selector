from info_prep import get_project_list
import config
from collections import OrderedDict


def main():
    print("Reading {}/all.lzma file...".format(config.which_wiki))
    projects = get_project_list()
    ordered_projects = OrderedDict(sorted(projects.items(), key=lambda t: t[1], reverse=True))
    print("All projects read in, there are {} projects in the {} wiki.".format(len(ordered_projects),
                                                                               config.which_wiki))
    with open("Project-List-{}.txt".format(config.which_wiki), "w") as of:
        of.write("Project Name\tNumber Of Articles\n")
        for name, count in ordered_projects.items():
            try:
                of.write('{}\t{}\n'.format(name, count))
            except:
                print("Had to skip a project due to a non-unicode name.")


if __name__ == "__main__":
    main()
