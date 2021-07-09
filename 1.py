import os

paths = ''


def get_path(path_now,finds1tr):
    for path_re in os.listdir(path_now):
        # print(path_re)


        if os.path.isdir(path_now + '\\' + path_re):
            pathnow1 = path_now + '\\' + path_re
            # print(pathnow1)
            get_path(pathnow1,finds1tr)
        else:
            finds1tr = str(finds1tr)
            # print(path_re)
            # print(finds1tr, path_re)
            if finds1tr in path_re:
                print(2313,path_now)
path_now = os.getcwd()

get_path(path_now,'')