#! /usr/local/bin/python3
#! encoding=utf-8

import os
import shutil
import os.path
import sys
import subprocess
import zipfile
import time


def delete(path):
    """
    删除一个文件/文件夹,如果路径不存在，会输出错误并返回
    如果路径是一个文件夹，则会递归的删除里面的所有文件和子目录
    :param path: 待删除的文件路径
    :return: 无
    """
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

def insure_empty_dir(dir_path):
    """
    确保为一个空目录;
    如果已经存在，则先删除掉此目录后再次创建空目录;
    如果不存在，则直接创建空目录;
    :param dir_path: 待检查的文件夹路径
    :return: 无
    """
    if os.path.exists(dir_path):
        delete(dir_path)
    os.makedirs(dir_path)

def copy_dir(src, dst):
    """Copy directory src to dst

    :param src: eg. '/var/include'
    :param dst: eg. '/usr/local/xx-include'
    """
    import shutil
    shutil.rmtree(dst, ignore_errors=True)
    shutil.copytree(src, dst, symlinks=True)

def copy_file(src, dst):
    import shutil
    shutil.copy(src,dst)

def mergefolders(root_src_dir, root_dst_dir):
    for src_dir, dirs, files in os.walk(root_src_dir):
        dst_dir = src_dir.replace(root_src_dir, root_dst_dir, 1)
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
        for file_ in files:
            src_file = os.path.join(src_dir, file_)
            dst_file = os.path.join(dst_dir, file_)
            if os.path.exists(dst_file):
                os.remove(dst_file)
            shutil.copy(src_file, dst_dir)

def creation_date(path_to_file):
    """
    Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible.
    获取文件的创建时间，如果获取不到，则返回文件的最后修改时间。(适配了windows和非windows)
    :path_to_file: 文件地址
    :return: 创建时间,timemills
    See http://stackoverflow.com/a/39501288/1709587 for explanation.
    """
    import platform
    if platform.system() == 'Windows':
        return os.path.getctime(path_to_file)
    else:
        stat = os.stat(path_to_file)
        try:
            return stat.st_birthtime
        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            return stat.st_mtime

def get_time_str(timemills):
    return time.strftime("%Y-%m-%d, %H:%M:%S",time.localtime(timemills))

def get_environment_value(key):
    if key in os.environ:
        key = os.environ[key]
        return key

def run_os_cmd(command_string, silence = False):
    if not silence:
        print('run_os_cmd: {}'.format(command_string))
    result = os.system(command_string)
    if result != 0:
        raise Exception('os.system fail, cmd:{}'.format(command_string))

def mount_sdk_dirs(username,password,ip,mount_remote_dir,mount_local_path):
    """
    挂载公司磁盘到本地
    mount_remote_dir: 这里是相对于公司磁盘根目录的地址
    mount_local_path: 挂载到本地电脑上的目录地址
    :return: 无
    """
    import urllib.parse
    username = urllib.parse.quote(username)
    password = urllib.parse.quote(password)
    ip = urllib.parse.quote(ip)

    if not os.path.exists(mount_local_path):
        os.makedirs(mount_local_path)
    if os.path.ismount(mount_local_path):
        print('{0} is mounted,umount first...'.format(mount_local_path))
        umount_share(mount_local_path)
    else:
        insure_empty_dir(mount_local_path)
        run_os_cmd('mount -t smbfs //{0}:{1}@{2}/{3} {4}'.format(username,password,ip,mount_remote_dir,mount_local_path),True)

def umount_share(mount_local_path):
    """
    mount_local_path: 已经挂载了磁盘的本地文件夹地址
    """
    run_os_cmd("umount -fv {0}".format(mount_local_path),True)

def if_path_mounted(path):
    return os.path.ismount(path)

def get_zip_file(input_path, result):
    """
    对目录进行遍历，用于压缩文件夹
    :param input_path:
    :param result:
    :return:
    """
    files = os.listdir(input_path)
    for file in files:
        if os.path.isdir(input_path + '/' + file):
            get_zip_file(input_path + '/' + file, result)
        else:
            result.append(input_path + '/' + file)
 
 
def zip_file_path(input_path, output_path, output_name):
    """
    压缩文件夹
    :param input_path: 要压缩的文件夹的路径
    :param output_path: 输出zip的文件夹的路径
    :param output_name: zip压缩包名称
    :return:
    """
    f = zipfile.ZipFile(output_path + '/' + output_name, 'w', zipfile.ZIP_DEFLATED)
    filelists = []
    get_zip_file(input_path, filelists)
    for file in filelists:
        f.write(file)
    # 调用了close方法才会保证完成压缩
    f.close()
    return output_path + r"/" + output_name

def unzip_file(zip_file_path,dst_path):
    """
    解压zip到指定目录下，
    zip_file_path: zip文件地址
    dst_path: 指定目录地址
    """
    zFile = zipfile.ZipFile(zip_file_path, "r") 
    for fileM in zFile.namelist(): 
        zFile.extract(fileM, os.path.join(dst_path))
    zFile.close()

def upload_pgyer(userKey,apiKey,apk_file_path,password=""):
    # 1：公开安装，2：密码安装
    if len(password.strip())>0:
        install_type = 2
    else :
        install_type = 1
   
    pgy_site = 'https://www.pgyer.com/apiv2/app/upload'

    upload_command = 'curl -F "file=@{0}" -F "_api_key={1}" -F "buildInstallType={2}" -F "buildPassword={3}" {4}'.format(os.path.realpath(apk_file_path), apiKey, install_type, password, pgy_site)


    print ("<< upload command {0}".format(upload_command))

    run_os_cmd(upload_command,True)

def load_json_from_file(file_path):
    import json
    libs_json = json.load(file_path, 'r')
    return libs_json

def write_json_to_file(libs_json,file_path):
    import json
    with open(file_path,'w') as f:
        json.dump(libs_json,f,indent=4)


desktop = os.path.join(os.environ['HOME'],'Desktop')
script_path = os.path.dirname(os.path.realpath(__file__))
