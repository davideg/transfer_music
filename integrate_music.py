import os
import argparse
import cPickle as pickle
import gzip
from shutil import copy2

INDEX_FILE = '.musicdestindex.{0}.index'
IGNORE_ARTICLES = ['the', 'el', 'los', 'las', 'le', 'les', 'la']

def _get_index_file_name(dest_dir):
    def ord3(ch):
        return '%.3d' % ord(ch)
    hash_num = (''.join(map(ord3, os.path.normpath(dest_dir))))
    return INDEX_FILE.format(hash_num)

def _build_index(dest_dir):
    music_index = _load_index(dest_dir) or {}
    if not music_index:
        artists = (d for d in os.listdir(dest_dir)
                     if os.path.isdir(os.path.join(dest_dir, d)))
        for artist in artists:
            music_index[artist] = {}
            albums = (d for d in os.listdir(os.path.join(dest_dir, artist))
                        if os.path.isdir(os.path.join(dest_dir, artist, d)))
            for album in albums:
                songs = [s for s in os.listdir(os.path.join(dest_dir, artist, album))
                           if os.path.isfile(os.path.join(dest_dir, artist, album, s))]
                music_index[artist][album] = songs
    return music_index

def _load_index(dest_dir):
    music_index = None
    index_file = _get_index_file_name(dest_dir)
    if os.path.isfile(index_file):
        with gzip.open(index_file, 'rb') as f:
            music_index = pickle.load(f)
    return music_index

def _save_index(dest_dir, music_index):
    index_file = _get_index_file_name(dest_dir)
    if os.path.isfile(index_file):
        copy2(index_file, index_file + '.bak')
    with gzip.open(index_file, 'wb') as f:
        pickle.dump(music_index, f, pickle.HIGHEST_PROTOCOL)

def integrate_music(music_index, dest_dir, source_dirs):
    pass

def main():
    parser = argparse.ArgumentParser(description='Copy music from several'
                                     ' source directories into a single'
                                     ' directory taking care not to add any'
                                     ' music that already appears in the'
                                     ' destination directory')
    parser.add_argument('--src', metavar='<source dir>', action='append',
                        dest='source_dirs',
                        help='source directory containing directories in the'
                        ' format <artist>/<album> (default is current working'
                        ' directory)')
    parser.add_argument('dest_dir')

    args = parser.parse_args()
    if args.source_dirs is None:
        args.source_dirs = [os.getcwd()]
    music_index = _build_index(args.dest_dir)
    integrate_music(music_index, args.dest_dir, args.source_dirs)
    _save_index(args.dest_dir, music_index)


if __name__ == '__main__':
    main()
