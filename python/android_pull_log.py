#! /usr/local/bin/python3
#! encoding=utf-8

from cmath import e
import os
import sys

def delete(path):
    """
    删除一个文件/文件夹,如果路径不存在，会输出错误并返回
    如果路径是一个文件夹，则会递归的删除里面的所有文件和子目录
    :param path: 待删除的文件路径
    :return: 无
    """
    import shutil
    if not os.path.exists(path):
        print ("[*] {} not exists".format(path))
        return

    if os.path.isdir(path):
        shutil.rmtree(path)
    elif os.path.isfile(path):
        os.remove(path)
    elif os.path.islink(path):
        os.remove(path)
    else:
        print ("[*] unknow type for: " + path)

def run_os_cmd(command_string, silence = False):
    if not silence:
        print('run_os_cmd: {}'.format(command_string))
    result = os.system(command_string)
    if result != 0:
        raise Exception('os.system fail, cmd:{}'.format(command_string))

def get_apk_log_files(package_name,dst_path):
    delete(dst_path)
    run_os_cmd('adb pull /sdcard/Android/data/{0}/files {1}'.format(package_name,dst_path))
    
def get_apk_log_files_to_desktop(package_name):
    get_apk_log_files(package_name,'~/Desktop/{}'.format(package_name))

if __name__ =='__main__':
    if len(sys.argv) > 1:
        get_apk_log_files_to_desktop(sys.argv[1])
            


