# moves .bnk not used in .txtp to 'unwanted' folder
#
# ex.
#   ./wem/music.bnk #1
#   # Autogenerated blah blah
#   # - events.bnk
#   will move anything that isn't music.bnk and events.bnk (plus ignored init.bnk)

#todo improve mixed case (.BNK will be moved to .bnk)

import glob, os, re, sys

move_dir = 'unwanted-bnk'
default_dir = 'wem'

# put filenames to print on which .txtp they are referenced
targets = []
targets_done = {}
if len(sys.argv) > 1:
    for i in range(1, len(sys.argv)):
        targets.append(sys.argv[i].lower())

#todo never move init.bnk

def main():
    # folders are taken from .txtp (meaning with no .txtp moves nothing)
    glob_folders = set() #set(['wem', 'sound', 'audio'])
    # fixed list since folders may have more extensions than those used in .txtp
    glob_exts = ['bnk']
    # base txtps
    glob_txtps = '*.txtp'

    # catch folder-like parts followed by name + extension
    pattern1 = re.compile(r"^[ ]*[?]*[ ]*([0-9a-zA-Z_\- \\/\.]*[0-9a-zA-Z_]+\.[0-9a-zA-Z_]+).*$")
    # catch comment with .bnk used to generate current .txtp
    pattern2 = re.compile(r"^#[ ]*-[ ]*([0-9a-zA-Z_\- \\/\.]*[0-9a-zA-Z_]+\.bnk).*$")

    # wems in txtp
    txtps = glob.glob(glob_txtps)
    files_used = set()
    last_path = default_dir
    for txtp in txtps:
        with open(txtp, 'r', encoding='utf-8-sig') as infile:
            for line in infile:
                #
                if line.startswith('#'):
                    match = pattern2.match(line)
                else:
                    match = pattern1.match(line)
                if match:
                    name, = match.groups()
                    file = os.path.normpath(name)
                    file = os.path.normcase(file)

                    # todo detect last_path better (or use all paths) 
                    if line.startswith('#') and '.bnk' in file:
                        file = os.path.join(last_path, file)

                    path = os.path.dirname(file)
                    files_used.add(file.strip())
                    glob_folders.add(path.strip())
  
                    last_path = path.strip()

                    if targets:
                        basename = os.path.basename(name.lower().strip())
                        basename = os.path.splitext(basename)[0]
                        if basename in targets_done:
                            continue
                        targets_done[basename] = True
                        for target in targets:
                            if basename.endswith(target):
                                print("file %s in %s" % (target, txtp))

    if targets:
        print("done")
        return

    # bnks in folders
    files_move = {}
    for glob_folder in glob_folders:
        for glob_ext in glob_exts:
            glob_search = os.path.join(glob_folder, '*.%s' % (glob_ext))
            files = glob.glob(glob_search)
            for file in files:
                path = os.path.normpath(file)
                path = os.path.normcase(path)
                files_move[path] = file

    # remove used from folders
    for file_used in files_used:
        if file_used in files_move:
            files_move.pop(file_used)

    # move remaining in folders = unused
    count = 0
    for _, file_move in files_move.items():
        ignore = False
        for bnk in ['init.bnk', '1355168291.bnk']:
            if bnk in file_move.lower():
                ignore = True
                continue
        if ignore:
            continue

        #move .bnk and companion files if any
        for ext in ['.bnk', '.txt', '.xml','.json']:
            file_base = file_move.replace('.bnk', ext)

            file_unwanted = os.path.join(move_dir, file_base)

            try:
                print("moving:", file_unwanted)
                os.makedirs(os.path.dirname(file_unwanted), exist_ok=True)
                os.rename(file_base, file_unwanted)
                #print(file_base, file_unwanted)
                count += 1
            except:
                pass #ignore not companion

    print("moved %i" % (count))
    #input()

if __name__ == "__main__":
    main()
