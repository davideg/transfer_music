import logging
import os
import argparse
import cPickle as pickle
import gzip
from shutil import copy2

DEFAULT_LOGGING_LEVEL = logging.INFO
INDEX_FILE = '.musicdestindex.{0}.index'
IGNORE_ARTICLES = ['the', 'el', 'los', 'las', 'le', 'les', 'la']

def _get_index_file_name(music_dir):
    def ord3(ch):
        return '%.3d' % ord(ch)
    hash_num = (''.join(map(ord3, os.path.normpath(music_dir))))
    return INDEX_FILE.format(hash_num)

def _build_index(music_dir):
    music_index = _load_index(music_dir) or {}
    if not music_index:
        artists = (d for d in os.listdir(music_dir)
                     if os.path.isdir(os.path.join(music_dir, d)))
        for artist in artists:
            normalized_artist = _normalize_name(artist)
            music_index[normalized_artist] = {}
            albums = (d for d in os.listdir(os.path.join(music_dir, artist))
                        if os.path.isdir(os.path.join(music_dir, artist, d)))
            for album in albums:
                songs = [_normalize_name(s, remove_extension=True)
                         for s in os.listdir(os.path.join(music_dir, artist,
                                                          album))
                         if os.path.isfile(os.path.join(music_dir, artist,
                                                        album, s))]
                music_index[artist][_normalize_name(album)] = songs
    return music_index

def _load_index(music_dir):
    music_index = None
    index_file = _get_index_file_name(music_dir)
    if os.path.isfile(index_file):
        with gzip.open(index_file, 'rb') as f:
            music_index = pickle.load(f)
    return music_index

def _save_index(music_dir, music_index):
    index_file = _get_index_file_name(music_dir)
    if os.path.isfile(index_file):
        copy2(index_file, index_file + '.bak')
    with gzip.open(index_file, 'wb') as f:
        pickle.dump(music_index, f, pickle.HIGHEST_PROTOCOL)

def integrate_music(music_index, dest_dir, source_dirs, dry_run=False):
    pass

def _normalize_name(possible_path, remove_extension=False):
    name = os.path.basename(possible_path).strip().lower()
    name = re.sub('^\d\d?-', '', name, count=1)
    name = re.sub('^\d* *-? +', '', name, count=1)
    name = re.sub(r'^\b(?:' + '|'.join(IGNORE_ARTICLES) + r')\b', '', name, count=1)
    name = name.replace('_', ' ')
    if remove_extension:
        name = os.path.splitext(name)[0]
    return name.strip()

def _setup_logging(verbose=False):
    logging_level = DEFAULT_LOGGING_LEVEL
    if verbose:
        logging_level = logging.DEBUG
    logger = logging.getLogger('integrate_music')
    logger.propagate = 0
    logger.setLevel(logging_level)
    handler = logging.StreamHandler()
    handler.setLevel(logging_level)
    logger.addHandler(handler)

def main():
    parser = argparse.ArgumentParser(description='Copy music from several'
                                     ' source directories into a single'
                                     ' directory taking care not to add any'
                                     ' music that already appears in the'
                                     ' destination directory (or a different'
                                     ' directory containing a music library'
                                     ' if specified)')
    parser.add_argument('--src', metavar='<source dir>', action='append',
                        dest='source_dirs',
                        help='source directory containing directories in the'
                        ' format <artist>/<album> (default is current working'
                        ' directory)')
    parser.add_argument('--music-dir', metavar='<music dir>', dest='music_dir',
                        help='directory that contains the music library.'
                        ' Music from a source directory that is identical to'
                        ' music found in this directory will not be added to'
                        ' the destination directory')
    parser.add_argument('--dry-run', dest='dry_run', action='store_true',
                        default=False,
                        help='perform a trial run with no changes made.'
                        ' Index of music directory is still created and saved')
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true',
                        default=False, help='turn on debugging logging')
    parser.add_argument('dest_dir')

    args = parser.parse_args()
    _setup_logging(args.verbose)
    source_dirs = args.source_dirs or [os.getcwd()]
    music_dir = args.music_dir or args.dest_dir
    music_index = _build_index(music_dir)
    integrate_music(music_index, args.dest_dir, source_dirs,
                    dry_run=args.dry_run)
    _save_index(music_dir, music_index)


if __name__ == '__main__':
    main()
