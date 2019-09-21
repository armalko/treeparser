import os
from time import time, sleep
import datetime


class treeparser:

    def __init__(self):
        self.tree = {}
        self.root = ''
        self.update_time = -1

    def __contains__(self,
                     item):
        try:
            self.__getitem__(item)
            return True
        except KeyError:
            return False

    def __getitem__(self,
                    item):
        tree = self.tree
        if item == '':
            return tree
        for fol in item.split('/'):
            tree = tree[fol]
        return tree

    def __str__(self):
        return treeparser.__print_folder__(self.tree, step=0)

    def check(self):
        return self.update()

    def print_updates(self, delay=0.5, duration=50, file=''):
        start_time = time()
        while True:
            if time() - start_time < duration:
                upd = self.update()
                now = datetime.datetime.now()
                if upd['del_dirs'] or upd['created_dirs'] or upd['del_files'] or upd['created_files']:
                    print("{}:{}:{}: Update: {}".format(str(now.hour),
                                                        str(now.minute), str(now.second), str(upd)))
                    if file:
                        with open(file, 'a') as f:
                            f.write("{}:{}:{}: Update: {}\n".format(str(now.hour),
                                                                    str(now.minute), str(now.second), str(upd)))
                sleep(delay)
            else:
                break

    @staticmethod
    def __print_folder__(tree,
                         step):
        string = ''
        folders = []
        files = []
        for key in tree:
            if '1514_F_' in key:
                files.append(key)
            else:
                folders.append(key)

        # print('Files: {}, Folders: {}'.format(files, folders))
        for f in (range(len(files))):
            if not(f == len(files) - 1):
                string += ('|'+'---'*step + files[f][7:] + '\n')
            else:
                string += ('∟'+'---'*step + files[f][7:] + '\n')
        for f in folders:
            string += ('\t'*step + f + '\n')
            string += treeparser.__print_folder__(tree[f], step=step+1)

        return string

    @staticmethod
    def __update_folder__(tree,
                          root,
                          cpath):
        folders = []
        files = []
        del_dirs = []
        del_files = []

        for key in tree:
            if '1514_F_' in key:
                files.append(key)
            else:
                folders.append(key)

        for f in files:
            if not(os.path.isfile(root + cpath + f[7:])):
                del_files.append(cpath + f)

        for f in folders:
            if not(os.path.isdir(root + cpath + f)):
                del_dirs.append(cpath + f)
            else:
                dic = treeparser.__update_folder__(tree[f], root, cpath + f + '/')
                del_dirs.extend(dic['dirs'])
                del_files.extend(dic['files'])
        return {'dirs': del_dirs, 'files': del_files}

    def __add_file__(self,
                     path,
                     file_name):
        tree = self[path]
        file_info = os.stat(self.root + path + '/' + file_name)
        tree['1514_F_' + file_name] = {'mtime': file_info[-2]}

    def __add_folder__(self,
                       path,
                       folder_name):
        tree = self[path]
        tree[folder_name] = {}

    def __del_file__(self,
                     path,
                     file_name):
        tree = self[path]
        if '1514_F_' + file_name in tree:
            del tree['1514_F_' + file_name]
        else:
            print('No such file: {}'.format('1514_F_' + file_name))

    def __del_folder__(self,
                       path):
        if not('/' in path):
            del self.tree[path]
            return None
        name = path[path.rfind('/') + 1:]
        tree = self[path[:path.rfind('/')]]
        if name in tree:
            del tree[name]
        else:
            print('No such folder: {}'.format(name))

    def fill(self,
             path):
        self.root = path

        for current_path, folders, files in os.walk(path):
            local_path = current_path.replace(self.root, '')
            for folder in folders:
                self.__add_folder__(local_path, folder)
            for file in files:
                self.__add_file__(local_path, file)

        self.update_time = time()

    def update(self):
        created_dirs = []
        created_files = []
        for current_path, folders, files in os.walk(self.root):
            local_path = current_path.replace(self.root, '')

            if local_path == '':
                lp = ''
            else:
                lp = local_path + '/'

            for folder in folders:
                if not(lp + folder in self):
                    self.__add_folder__(local_path, folder)
                    created_dirs.append(lp + folder)
            for file in files:
                if not(lp + '1514_F_' + file in self):
                    self.__add_file__(local_path, file)
                    created_files.append(lp + file)
                elif os.stat(current_path + '/' + file)[-2] > self[lp + '1514_F_' + file]['mtime']:
                    self.__del_file__(local_path, file)
                    self.__add_file__(local_path, file)
                    created_files.append(lp + file)

        update_check = treeparser.__update_folder__(self.tree, self.root, '')

        for d in update_check['dirs']:
            self.__del_folder__(d)

        for file in update_check['files']:
            name = file[file.rfind('/') + 1:][7:]
            self.__del_file__(file[:file.rfind('/') + 1], name)

        self.update_time = time()
        return {'del_dirs': update_check['dirs'],
                'created_dirs': created_dirs,
                'del_files': update_check['files'],
                'created_files': created_files
                }

