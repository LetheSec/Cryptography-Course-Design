import os
import sys
import time
import random
import string
import socket
import libnum
from Hash.md5 import md5
from base64 import b64encode
import BlockCipher.DES as DES
import PublickeyCipher.RSA as RSA
import PublickeyCipher.DigitalSignature as DigitalSigna
##########################################################################################
SERVER_WORKDIR = "F:\\MyCode\\Cryptography\\FileTransferSystem\\ServerData\\"
SERVER_PUB_PATH = "F:\\MyCode\\Cryptography\\FileTransferSystem\\ServerKeys\\server.pub"
SERVER_KEY_PATH = "F:\\MyCode\\Cryptography\\FileTransferSystem\\ServerKeys\\server.key"
CLIENT_PUB_PATH = "F:\\MyCode\\Cryptography\\FileTransferSystem\\ServerKeys\\client.pub"
MAXBUFFSIZE = 51200
BUFFSIZE = 20480
SERVER_ADDRESS = ("127.0.0.1", 12345)
##########################################################################################

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.bind(SERVER_ADDRESS)
serverSocket.listen(3)


def get_des_param():
    """
    产生64位随机的key和IV
    :return:
    """
    while True:
        key = ''.join(random.sample(string.ascii_letters + string.digits, 8))
        IV = ''.join(random.sample(string.ascii_letters + string.digits, 8))
        if key != IV:
            break
    return key, IV


def get_file_md5(filepath):
    """
    对文件内容进行md5产生消息摘要来确保文件传输过程中的完整性
    :param filepath: 文件路径
    :return: 文件摘要
    """
    with open(filepath, 'rb') as fs:
        digest = md5(fs.read().decode('latin'))
    return digest


def get_private_key(keypath):
    """
    从文件中读取
    :param keypath: 私钥文件地址
    :return: 私钥d
    """
    with open(keypath, 'r') as f:
        d = int(f.read())
    return d


def check_file_sign(filepath, sign):
    with open(filepath, 'rb') as fs:
        filedata = b64encode(fs.read()).decode()
        sign = str(sign).strip()
        res = DigitalSigna.check(filedata, sign, server_e, server_n)
    return res


def get_public_key(keypath):
    """
    从文件中读取公钥
    :param keypath: 公钥文件地址
    :return: e, n
    """
    with open(keypath, 'r') as f:
        keys = f.readlines()
        e = int(keys[0])
        n = int(keys[1])
    return e, n


# 用于打印传输进度条的函数
def progress_bar(loaded, total):
    ratio = float(loaded) / total
    percentage = int(ratio * 100)
    r = '\r[%s%s]%d%%' % (">" * percentage, " " * (100 - percentage), percentage)
    sys.stdout.write(r)
    sys.stdout.flush()


# 列出工作目录下的所有文件相对路径
def get_filelist(path):
    allfiles = []
    if not os.path.exists(path):
        return -1
    for root, dirs, names in os.walk(path):
        for filename in names:
            allfiles.append(os.path.join(root, filename).replace(path, ''))
    return allfiles


def file_encrypt(filepath):
    """
    对文件进行DES-CBC加密,并用RSA加密key和iv
    :param filepath: 原文件路径
    :return: 加密文件路径, 原文件md5值, 加密后的key, 加密后的iv
    """
    # 随机生成key和iv
    key, iv = get_des_param()
    # 打开原文件
    origin_file = open(filepath, 'rb')
    origin_filedata = origin_file.read().decode('latin')
    # 计算原文件的消息摘要
    origin_digest = md5(origin_filedata)
    # 加密后文件的地址(统一加上.encrypted后缀)
    encrypted_filepath = filepath + ".encrypted"
    # 写入加密文件
    encrypted_file = open(encrypted_filepath, 'wb')
    encrypted_file.write(DES.des_cbc_encrypt(origin_filedata, key, iv).encode('latin'))
    # 关闭文件
    origin_file.close()
    encrypted_file.close()
    # 用client的公钥对key和iv进行加密
    key_encrypted = RSA.Encrypt(libnum.s2n(key), client_e, client_n)
    iv_encrypted = RSA.Encrypt(libnum.s2n(iv), client_e, client_n)
    return encrypted_filepath, origin_digest, key_encrypted, iv_encrypted


def file_decrypt(encrypted_filepath, key_encrypted, iv_encrypted):
    """
    对文件进行解密
    :param encrypted_file_path: 加密文件的路径
    :param key_encrypted: 加密的密钥
    :param iv_encrypted: 加密的iv
    :return: 解密后文件路径, 解密后文件的md5
    """
    # 先用server的私钥对key和iv进行解密
    key = RSA.Decrypto(key_encrypted, server_d, server_d)
    iv = RSA.Decrypto(iv_encrypted, server_d, server_d)
    # 打开并读取加密文件
    encrypted_file = open(encrypted_filepath, 'rb')
    encrypted_filedata = encrypted_file.read().decode('latin')
    # 去掉.crypted后缀
    origin_filepath = ".".join(encrypted_filepath.split('.')[:-1])
    # 将解密后的内容写入新文件
    origin_file = open(origin_filepath, 'wb')
    origin_file.write(DES.des_cbc_decrypt(encrypted_filedata, libnum.n2s(key), libnum.n2s(iv)).encode('latin'))
    # 关闭文件指针
    encrypted_file.close()
    origin_file.close()
    # 计算解密后文件的md5消息摘要
    origin_file_digest = get_file_md5(origin_filepath)
    return origin_filepath, origin_file_digest


def transfer_encrypt(message):
    """
    对分组传输的每一个分组进行des_cbc加密,且每次使用不同的key和iv
    :param message: 被加密的分组
    :return: key,iv,cipher
    """
    key, iv = get_des_param()
    cipher = DES.des_cbc_encrypt(message, key, iv, 'b')
    # 用client的公钥对key和iv进行加密
    key_encrypted = RSA.Encrypt(libnum.s2n(key), client_e, client_n)
    iv_encrypted = RSA.Encrypt(libnum.s2n(iv), client_e, client_n)
    return key_encrypted, iv_encrypted, cipher


def transfer_decrypt(cipehr, key_encrypted, iv_encrypted):
    """
    对接收到的每一个分组进行解密
    :param cipehr: 收到的加密分组
    :param key_encrypted: 收到的加密过的key
    :param iv_encrypted: 收到的加密过的iv
    :return: 明文
    """
    # 先用server的私钥对key和iv进行解密
    key = RSA.Decrypto(key_encrypted, server_d, server_d)
    iv = RSA.Decrypto(iv_encrypted, server_d, server_d)
    # 用key和iv对收到的密文分组解密
    message = DES.des_cbc_decrypt(cipehr, libnum.n2s(key), libnum.n2s(iv), 'b')
    return message


# 打印出工作目录中可以进行传输的文件
def send_filelist(path):
    fileslist = get_filelist(path)
    print("*********************************************************************************************************")
    print("List file:")
    for i in fileslist:
        print(i)
    fileslist_str = '*'.join(fileslist)
    # 进行md5消息摘要
    fileslist_digest = md5(fileslist_str)
    # 对发送的要发送的内容(文件列表)进行des-cbc加密
    key_encrypted, iv_encrypted, allfiles_encrypted = transfer_encrypt(fileslist_str)
    # 发送RSA加密后的key
    mainSocket.send(str(key_encrypted).encode())
    time.sleep(0.01)
    # 发送RSA加密后的iv
    mainSocket.send(str(iv_encrypted).encode())
    time.sleep(0.01)
    # 发送des-cbc加密后的内容
    mainSocket.send(allfiles_encrypted.encode())
    time.sleep(0.01)
    # 发送消息摘要
    mainSocket.send(fileslist_digest.encode())
    time.sleep(0.01)
    print("The list of optional files was successfully sent")
    print("*********************************************************************************************************")
    return 0


# 处理客户端的文件下载请求
def get_file(filename):
    print("\n*********************************************************************************************************")
    # 确定文件路径
    filepath = SERVER_WORKDIR + filename
    print("Send: " + filepath)
    """
    接收客户端的连接请求
    """
    if os.path.isfile(filepath):
        # 对该文件进行加密,并计算初始md5值
        encrypted_filepath, file_digest, encrypted_key, encrypted_iv = file_encrypt(filepath)
        # 获取文件大小
        file_size = str(os.path.getsize(encrypted_filepath))
        # 发送文件的大小
        mainSocket.send(file_size.encode())
        time.sleep(0.1)
        # 定义已发送的文件大小
        send_size = 0

        # 打开该加密文件
        f = open(encrypted_filepath, 'rb')
        print("Start transferring...")
        # 循环发送文件
        while True:
            filedata = f.read(MAXBUFFSIZE).decode()
            # 如果文件全部发送玩,则break
            if not filedata:
                break
            mainSocket.send(filedata.encode())
            while True:
                confirm = mainSocket.recv(10).decode()
                if confirm == "yes":
                    break
            send_size += len(filedata)
            progress_bar(send_size, int(file_size, 10))
        print("\nGet the file Successfully.")
        f.close()
        # 删除生成的临时加密文件
        os.remove(encrypted_filepath)
        # 发送加密后的key
        mainSocket.send(str(encrypted_key).encode())
        while True:
            confirm = mainSocket.recv(10).decode()
            if confirm == "yes":
                break
        # 发送加密后的iv
        mainSocket.send(str(encrypted_iv).encode())
        while True:
            confirm = mainSocket.recv(10).decode()
            if confirm == "yes":
                break
        # 发送原文件md5
        mainSocket.send(file_digest.encode())
        while True:
            confirm = mainSocket.recv(10).decode()
            if confirm == "yes":
                break
    else:
        print("[Error]: Cat't find the file")
        mainSocket.send("0".encode())
    print("*********************************************************************************************************\n")
    return 0


# 处理客户端的文件下载请求
def get_file_stream(filename):
    print("\n*********************************************************************************************************")
    # 确定文件路径
    filepath = SERVER_WORKDIR + filename
    print("Send: " + filepath)

    if os.path.isfile(filepath):
        file_size = str(os.path.getsize(filepath))
        mainSocket.send(file_size.encode())
        while True:
            confirm = mainSocket.recv(10).decode()
            if confirm == "yes":
                break
        # 总共要传输的次数
        count = (int(file_size) // BUFFSIZE) + 1

        # 获得原文件的md5
        file_digest = get_file_md5(filepath)
        send_size = 0
        f = open(filepath, 'rb')
        print("Start transferring...")
        # 循环发送文件
        while count:
            filedata = b64encode(f.read(BUFFSIZE)).decode()
            key_encrypted, iv_encrypted, allfiles_encrypted = transfer_encrypt(filedata)
            # 发送des-cbc加密后的内容(16进制)
            mainSocket.send(allfiles_encrypted.encode())
            while True:
                confirm = mainSocket.recv(10).decode()
                if confirm == "yes":
                    break
            # 发送RSA加密后的key(10进制)
            mainSocket.send(str(key_encrypted).encode())
            while True:
                confirm = mainSocket.recv(10).decode()
                if confirm == "yes":
                    break
            # 发送RSA加密后的iv
            mainSocket.send(str(iv_encrypted).encode())
            while True:
                confirm = mainSocket.recv(10).decode()
                if confirm == "yes":
                    break
            # time.sleep(0.2)
            # 计算已发送的大小
            send_size += BUFFSIZE
            if send_size > int(file_size):
                send_size = file_size
            progress_bar(send_size, int(file_size, 10))
            count -= 1
        print("\nGet the file Successfully.")
        f.close()
        # 发送md5
        mainSocket.send(file_digest.encode())
        while True:
            confirm = mainSocket.recv(10).decode()
            if confirm == "yes":
                break
    else:
        print("[Error]: Cat't find the file")
        mainSocket.send("0".encode())
    print("*********************************************************************************************************\n")
    return 0


def main():
    global server_e, server_n, server_d, client_e, client_n
    server_e, server_n = get_public_key(SERVER_PUB_PATH)
    server_d = get_private_key(SERVER_KEY_PATH)
    client_e, client_n = get_public_key(CLIENT_PUB_PATH)
    while True:
        print("Waiting for connection...")
        global mainSocket
        mainSocket, addr = serverSocket.accept()
        cmdinfo = '''
Input one of the following command:
[+] list  ------------------------------------list the file
[+] get1 [filename] -----------------get the file by stream
[+] get2 [filename] -------------get the file after encrypt
[+] exit -----------------------------close socket and exit'''
        mainSocket.send(cmdinfo.encode())
        while True:
            recv_cmd = mainSocket.recv(BUFFSIZE).decode()
            if not recv_cmd:
                print("Not received.")
                break
            recv_cmd_list = recv_cmd.split()
            print("received command:" + recv_cmd_list[0] + "\n")
            if recv_cmd_list[0] == 'list' and len(recv_cmd_list) == 1:
                send_filelist(SERVER_WORKDIR)
            elif recv_cmd_list[0] == 'get1' and len(recv_cmd_list) == 2:
                get_file_stream(recv_cmd_list[1])
            elif recv_cmd_list[0] == 'get2' and len(recv_cmd_list) == 2:
                get_file(recv_cmd_list[1])
            elif recv_cmd_list[0] == 'exit' and len(recv_cmd_list) == 1:
                mainSocket.close()
                serverSocket.shutdown(2)
                break
    serverSocket.close()


if __name__ == '__main__':
    main()
