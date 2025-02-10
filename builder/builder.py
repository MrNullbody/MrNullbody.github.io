from compile import compile
import argparse
import os
import config
from tqdm import tqdm
import time
import shutil
import traceback

def list_files(filepath, filetype = ''):
    paths = []
    for root, dirs, files in os.walk(filepath):
        for file in files:
            if file.lower().endswith(filetype.lower()):
                paths.append((root, os.path.join(os.path.relpath(root, filepath), file)))
    return(paths)

if __name__ == '__main__':

    cur_dir = os.path.abspath(os.path.dirname(__file__))

    project_source_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    default_source_folder = os.path.join(project_source_folder, 'src')

    parser = argparse.ArgumentParser(description = 'The builder of a btex-based static website.')
    parser.add_argument('-s', '--source', type = str, default = default_source_folder,
                        help = 'The directory of the folder to be checked and compiled, set to the whole source folder by default.')
    parser.add_argument('-f', '--force', action = 'store_true', default = False,
                        help = 'Compile all the source files, regardless of modify time.')
    args = parser.parse_args()

    args.source = os.path.relpath(args.source, default_source_folder)

    if args.source.startswith('..'):
        print(f"[FATAL] specified source folder is not a subfolder of the {default_source_folder}.")
        exit(1)

    if (not os.path.exists(args.source)) or (not os.path.isdir(args.source)):
        print(f"[FATAL] specified source folder is not a folder.")
        exit(1)

    template_time = os.path.getmtime(os.path.join(cur_dir, config.template_filename))

    try:
        with open(os.path.join(cur_dir, config.template_filename), 'r') as f:
            template_html = f.read()

        index = template_html.find(f'{config.btex_output_specifier}')

        if index == -1:
            print(f"[FATAL] Can not find {config.btex_output_specifier} in {config.template_filename}")

        output_wrapper_begin, _, output_wrapper_end = template_html.partition(f"{config.btex_output_specifier}")

    except Exception as e:
        print(f"[FATAL] Error openning template file:{config.template_filename}.")
        exit(1)

    source_files = list_files(os.path.join(default_source_folder, args.source), '')

    # print(source_files)

    actions = []
    
    for _, filename in source_files:
        
        file_prefix, ext = os.path.splitext(filename)

        # print(ext)
        
        if ext == config.btex_suffix:
            
            dst = os.path.relpath(os.path.join(config.dst_path, file_prefix + config.html_suffix), os.getcwd())

            filename = os.path.relpath(os.path.join('src', filename), os.getcwd())
            
            if args.force:
                actions.append((dst, filename, 'compile'))

            else:
                if os.path.exists(dst) and os.path.isfile(dst) and os.path.getmtime(filename) - os.path.getmtime(dst) <\
                    config.maximal_allowed_time_interval and template_time - os.path.getmtime(dst) <\
                    config.maximal_allowed_time_interval:
                    
                    print(f"[INFO] Skipping {filename}.")

                else:
                    actions.append((dst, filename, 'compile'))
        
        else:

            dst = os.path.relpath(os.path.join(config.dst_path, filename), os.getcwd())

            filename = os.path.relpath(os.path.join('src', filename), os.getcwd())
            
            if args.force:
                actions.append((dst, filename, 'copy'))

            else:
                
                if os.path.exists(dst) and os.path.isfile(dst) and os.path.getmtime(filename) - os.path.getmtime(dst) <\
                    config.maximal_allowed_time_interval:
                    
                    print(f"[INFO] Skipping {filename}.")

                else:
                    actions.append((dst, filename, 'copy'))

    if len(actions) == 0:
        print(f"[INFO] Exiting... Nothing has been changed.")
        exit(0)

    print()

    print('Actions'.center(20, '='))
    for dst, src, action in actions:
        print(f"{action.capitalize()} {src} to {dst}.")
    print(''.center(20, '='))
    print()

    user_confirmation = input('Proceed? (y/[n]): ')
    print()
    if user_confirmation.lower() != 'y':
        print(f"[INFO] Exiting... Nothing has been changed.")
        exit(0)

    tqdm_iter = tqdm(actions)

    for dst, src, action in tqdm_iter:
        
        tqdm_iter.set_description(f"{action.capitalize()} {src} to {dst}.")

        if action == 'copy':
            
            try:
                os.makedirs(os.path.dirname(os.path.join('.', dst)), exist_ok = True)
                shutil.copy2(src, dst)
            except Exception as e:
                log_file = os.path.join(project_source_folder, 'log', 'builder_error.txt')

                with open(log_file, 'w') as f:
                    f.write(traceback.format_exc())

                error = f'[FATAL] {str(e)} Log file has been written to {log_file}.'
                tqdm_iter.write(error)
                exit(1)
        else:
            try:
                os.makedirs(os.path.dirname(os.path.join('.', dst)), exist_ok = True)
                result = compile(src, output_wrapper_begin, output_wrapper_end)
                with open(dst, 'w') as f:
                    f.write(result)

            except Exception as e:
                
                log_file = os.path.join(project_source_folder, 'log', 'builder_error.txt')

                with open(log_file, 'w') as f:
                    f.write(traceback.format_exc())

                error = f'[FATAL] {str(e)} Log file has been written to {log_file}.'
                tqdm_iter.write(error)
                exit(1)
        
        tqdm_iter.write(f"[INFO] {action.capitalize()} {src} to {dst}.")
