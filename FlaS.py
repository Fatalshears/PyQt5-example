# UDN1HC

import subprocess
import shutil


def flash_software(p_flashable_items, p_flash_all_folder, p_canape, radar_type):

    for file_path in p_flashable_items:
        shutil.copy(file_path[0], p_flash_all_folder)

    joined_path = p_flash_all_folder + '\\' + 'flash_by_tool.cns'
    f = open(joined_path, 'w')

    f.write(r'ClearWriteWindow();')
    f.write('\n')
    f.write(f'{radar_type}.Online();')

    for file_name in p_flashable_items:
        f.write('\n')
        f.write(f'Write("Flashing {file_name[1]} ..... ");')
        f.write('\n')
        f.write(f'{radar_type}.DownloadFile("{file_name[1]}");')
        f.write('\n')
        f.write('Sleep(1000);')

    f.close()

    bat_file = p_flash_all_folder + '\\' + 'flash_by_tool.bat'
    fb = open(bat_file, 'w')
    my_cmd = p_flash_all_folder[:p_flash_all_folder.index(':')+1]
    fb.write(my_cmd)
    fb.write('\n')
    my_cmd = f'cd "{p_flash_all_folder}"'
    fb.write(my_cmd)
    fb.write('\n')
    my_cmd = f'"{p_canape}" -b flash_by_tool.cns'
    fb.write(my_cmd)
    fb.close()

    try:
        subprocess.call([bat_file])
        #subprocess.Popen(bat_file)
    except OSError:
        return False
    return True
