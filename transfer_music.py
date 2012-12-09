import subprocess
import optparse
import sys
import os.path
import re

MUSIC_FILES_RE = r'.*\.(?:mp3|ogg|oga|aac|m4a|flac|wav|wma|aif|aiff|ape|mpc|shn)'
MIN_FILE_COUNT = 4
RSYNC_CMD = 'rsync -rvz --progress {src}/* {dest}'

def shellquote(s):
    return '"' + s.replace('"', '\\"') + '"'

def transfer_music(src, dest):
    to_transfer = []
    dirs = [path for path in (os.path.join(src, d) for d in os.listdir(src)) if os.path.isdir(path)]
    for dr in dirs:
        albums = [path for path in (os.path.join(dr, d) for d in os.listdir(dr))
                       if os.path.isdir(path)]
        for album in albums:
            file_count = len([path for path in (os.path.join(album, e) for e in os.listdir(album)
                                                                       if re.match(MUSIC_FILES_RE, e))
                                   if os.path.isfile(path)])
            if file_count >= MIN_FILE_COUNT:
                to_transfer.append(os.path.join(dr, album))
    _do_transfer(to_transfer, src, dest)

def _do_transfer(to_transfer, src, dest):
    for dr in to_transfer:
        dest_dir = os.path.join(dest, os.path.relpath(dr, src))
        pieces = dest_dir.split(':')
        if len(pieces) == 2:
            host, path = pieces
            dest_dir = ':'.join([host, shellquote(shellquote(path))])
        else:
            dest_dir = shellquote(dest_dir)
        _create_remote_dir(dest_dir)
        rsync_cmd = RSYNC_CMD.format(src=shellquote(dr), dest=dest_dir)
        print 'Performing transfer using: {0}'.format(rsync_cmd)
        subprocess.call(rsync_cmd, shell=True)

def _create_remote_dir(path):
    cmd = 'mkdir -p {0}'.format(path)
    if ':' in path:
        server, path = path.split(':')
        if server:
            cmd = 'ssh {0} mkdir -p {1}'.format(server, path)
    print 'Creating remote directory using: {0}'.format(cmd)
    subprocess.call(cmd, shell=True)


if __name__ == '__main__':
    usage = '%prog [<src dir>] <destination dir>'
    parse = optparse.OptionParser(usage)
    options, args = parse.parse_args()
    if len(args) < 1:
        sys.stderr.write('ERROR: missing required arguments\n')
        parse.print_usage()
        sys.exit(1)
    elif len(args) == 1:
        src = os.getcwd()
        dest = args[0]
    elif len(args) == 2:
        src = args[0]
        dest = args[1]
    else:
        sys.stderr.write('ERROR: too many arguments')
        parse.print_usage()
        sys.exit(1)
    transfer_music(src, dest)
