
import os 
import argparse

# ----------------------------------------

def check_time(args):

    print()
    
    subfolders = os.listdir(args.folder)
    subfolders.sort()

    for sub in subfolders:
        
        full_sub = os.path.join(args.folder, sub)

        all_files = os.listdir(full_sub)
        all_files.sort()
        
        times = [os.path.getctime(os.path.join(full_sub, f)) for f in all_files]
        
        diff = max(times) - min(times)
        count = len(times)
        avg = diff / float(count)
        
        print(f"Folder {sub}: diff {diff/60:.02f} minutes ({diff:.02f} seconds), count {count}, avg {avg:.02f} seconds")

    print()

# ----------------------------------------

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Description')
    parser.add_argument('--folder', type=str, required=True)
    args, _ = parser.parse_known_args()

    check_time(args)