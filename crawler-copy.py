#!/apps/base/python3/bin/python
import os
import shutil
import sys
import subprocess

num_operations = 0

source = sys.argv[1]
dest = sys.argv[2]
backup = sys.argv[3]
overwrite = ''

if source.endswith('/'):
    source = source[:-1]
if dest.endswith('/'):
    dest = dest[:-1]
if backup.endswith('/'):
    backup = backup[:-1]

if len(sys.argv) > 4:
    overwrite = sys.argv[4]

if overwrite.lower() == '--overwrite' or overwrite.lower() == '-o':
    overwrite = True
else:
    overwrite = False

try:
    subprocess.call(['mkdir', '-p', dest])
    subprocess.call(['mkdir', '-p', backup])
except:
    pass

lensource = len(source.split('/')[1:])
lendest = len(dest.split('/')[1:])
lenbackup = len(backup.split('/')[1:])

def scantree(path):
    """Recursively yield DirEntry objects for given directory."""
    for entry in os.scandir(path):
        if entry.is_dir(follow_symlinks=False):
            yield from scantree(entry.path)
        else:
            yield entry


def walk_through(source, dest, overwrite, length):
    def walk_through_start(decorated_function):
        def wrapper():
            global num_operations
            num_operations = 0
            for root, dirs, files in os.walk(source):
                for a_file in files:
                    filename = '/'.join([root, a_file])
                    if len(root.split('/')[1:]) - length == 0:
                        dest_dir = dest
                    else:
                        dest_dir = '/'.join([dest, '/'.join(root.split('/')[length + 1:])])
                        try:
                            subprocess.call(['mkdir', '-p', dest_dir])
                        except:
                            pass
                    arguments = (filename, dest_dir, overwrite)
                    decorated_function(*arguments)
            return decorated_function
        return wrapper
    return walk_through_start

@walk_through(source, dest, overwrite, lensource)
def copy_files(filename, dest_dir, overwrite):
    dest_file = '/'.join([dest_dir, filename.split('/')[-1]])
    if overwrite or os.path.exists(dest_file) == False and os.path.isfile(filename):
        shutil.copy(filename, dest_dir)
        print('Copying: ' + str(filename) + ' To: ' + str(dest_dir))

@walk_through(dest, dest, overwrite, lendest)
def unzip_dest(filename, dest_dir, overwrite):
    global num_operations
    zipow = '-n'
    tarow = '-k'
    if overwrite:
        zipow = '-o'
        tarow = '--overwrite'
    if os.path.exists(filename + '.skip'):
        pass
    else:
        if filename.endswith('.tgz') or filename.endswith('.tar.gz'):
            try:
                subprocess.call(['mkdir', '-p', '{}/{}'.format(dest_dir, '_'.join(str(filename).split('/')[-1].split('.')[0:-1]))])
            except:
                pass
            subprocess.call(['tar', 'xzvf', filename, '-C', '{}/{}'.format(dest_dir, '_'.join(str(filename).split('/')[-1].split('.')[0:-1])), tarow])
            subprocess.call(['touch', filename + '.skip'])
            num_operations += 1
        elif filename.endswith('.zip'):
            try:
                subprocess.call(['mkdir', '-p', '{}/{}'.format(dest_dir, '_'.join(str(filename).split('/')[-1].split('.')[0:-1]))])
            except:
                pass
            subprocess.call(['unzip', zipow, filename, '-d', '{}/{}'.format(dest_dir, '_'.join(str(filename).split('/')[-1].split('.')[0:-1]))])
            subprocess.call(['touch', filename + '.skip'])
            num_operations += 1
    return(num_operations)

@walk_through(dest, backup, overwrite, lenbackup)
def copy_backup(filename, dest_dir, overwrite):
    dest_file = '/'.join([dest_dir, filename.split('/')[-1]])
    if overwrite or os.path.exists(dest_file) == False and os.path.isfile(filename):
        shutil.copy(filename, dest_dir)
        print('Copying: ' + str(filename) + ' To: ' + str(dest_dir))

if __name__ == '__main__':

    copy_files()

    while True:
        unzip_dest()
        if num_operations == 0:
            break
    subprocess.call([sys.path[0] + '/crawler-cleanup.sh', dest])

    copy_backup()
