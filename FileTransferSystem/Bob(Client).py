import os
import sys
import time
import random
import string
import socket
import libnum
from Hash.md5 import md5
from base64 import b64decode,b64encode
import BlockCipher.DES as DES
import PublickeyCipher.RSA as RSA
import PublickeyCipher.DigitalSignature as DigitalSigna
##########################################################################################
CLIENT_WORKDIR = "F:\\MyCode\\Cryptography\\FileTransferSystem\\ClientData\\"
CLIENT_PUB_PATH = "F:\\MyCode\\Cryptography\\FileTransferSystem\\ClientKeys\\client.pub"
CLIENT_KEY_PATH = "F:\\MyCode\\Cryptography\\FileTransferSystem\\ClientKeys\\client.key"
SERVER_PUB_PATH = "F:\\MyCode\\Cryptography\\FileTransferSystem\\ClientKeys\\server.pub"
MAXBUFFSIZE = 51200
BUFFSIZE = 40960
BUFFSIZE_SENT = 20480
SERVER_ADDRESS = ("127.0.0.1", 12345)
##########################################################################################


clientServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def get_des_param():
    """
    产生64位随机的key和IV
    :return: des密钥和cbc的初始向量iv
    """
    while True:
        key = ''.join(random.sample(string.ascii_letters + string.digits, 8))
        iv = ''.join(random.sample(string.ascii_letters + string.digits, 8))
        if key != iv:
            break
    return key, iv


def get_private_key(keypath):
    """
    从文件中读取
    :param keypath: 私钥文件地址
    :return: 私钥d
    """
    with open(keypath, 'r') as f:
        d = int(f.read())
    return d


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

def get_file_sign(filepath):
    with open(filepath, 'rb') as fs:
        digest = d(fs.read().decode('latin'))
    return digest


def get_file_md5(filepath):
    """
    对文件内容进行md5产生消息摘要来确保文件传输过程中的完整性
    :param filepath: 文件路径
    :return: 文件摘要
    """
    with open(filepath, 'rb') as fs:
        digest = md5(fs.read().decode('latin'))
    return digest


def check_file_sign(filepath, sign):
    with open(filepath, 'rb') as fs:
        filedata = b64encode(fs.read()).decode()
        sign = str(sign).strip()
        res = DigitalSigna.check(filedata, sign, server_e, server_n)
    return res


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
    key_encrypted = RSA.Encrypt(libnum.s2n(key), server_e, server_n)
    iv_encrypted = RSA.Encrypt(libnum.s2n(iv), server_e, server_n)
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
    key = RSA.Decrypto(key_encrypted, client_d, client_n)
    iv = RSA.Decrypto(iv_encrypted, client_d, client_n)
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
    # 用server的公钥对key和iv进行加密
    key_encrypted = RSA.Encrypt(libnum.s2n(key), server_e, server_n)
    iv_encrypted = RSA.Encrypt(libnum.s2n(iv), server_e, server_n)
    return key_encrypted, iv_encrypted, cipher


def transfer_decrypt(cipehr, key_encrypted, iv_encrypted):
    """
    对接收到的每一个分组进行解密
    :param cipehr: 收到的加密分组
    :param key_encrypted: 收到的加密过的key
    :param iv_encrypted: 收到的加密过的iv
    :return: 明文
    """
    # 先用client的私钥对key和iv进行解密
    key = RSA.Decrypto(key_encrypted, client_d, client_n)
    iv = RSA.Decrypto(iv_encrypted, client_d, client_n)
    # 用key和iv对收到的密文分组解密
    message = DES.des_cbc_decrypt(cipehr, libnum.n2s(key), libnum.n2s(iv), 'b')
    return message


# 接收服务端发来的文件列表
def recv_filelist():
    clientServer.settimeout(2)
    try:
        # 接收key
        key_encrypted = int(clientServer.recv(BUFFSIZE).decode())
        iv_encrypted = int(clientServer.recv(BUFFSIZE).decode())
        fileslist_encrypted = clientServer.recv(BUFFSIZE).decode()
        fileslist_digest = clientServer.recv(32).decode()
        fileslist_decrypted = transfer_decrypt(fileslist_encrypted, key_encrypted, iv_encrypted)
        print(
            "\n*********************************************************************************************************")
        print("The list of files:")
        if fileslist_digest != md5(fileslist_decrypted):
            print("[Error]: The package you received may be broken\n")
        else:
            fileslist = fileslist_decrypted.split("*")
            for file in fileslist:
                print(file)
            print(
                "*********************************************************************************************************")
    except ConnectionResetError:
        print("[Error]: Address is wrong.")
    except TimeoutError:
        print("[Error]: Timeout.")
    except:
        print("[Error]: Something is wrong.")
    return 0


# 从服务端下载文件
def get_file(filename):
    print("\n*********************************************************************************************************")
    print("The file is being encrypted, please wait...")
    start = time.time()
    """
    ...
    与服务端建立TCP连接
    ...
    """
    clientServer.settimeout(10000)
    # 首先得到下载的文件大小(为了传输大文件,因此要分组接收)
    try:
        file_size = clientServer.recv(MAXBUFFSIZE).decode()
        time.sleep(0.1)
        file_size = int(file_size, 10)
        if file_size > 0:
            # 接收到的加密保存位置
            encrypted_filepath = CLIENT_WORKDIR + filename + ".encrypted"
            f = open(encrypted_filepath, 'wb')
            # 已接收的文件大小
            recv_size = 0
            print("Start transferring...")
            # 循环接收文件
            while recv_size != file_size:
                # 如果还剩余的文件大小 > 一次接收的最大值
                if file_size - recv_size > MAXBUFFSIZE:
                    # 接收文件
                    encrypted_filedata = clientServer.recv(MAXBUFFSIZE).decode()
                    clientServer.send("yes".encode())
                    recv_size += len(encrypted_filedata)
                    # 写入本地文件中
                    f.write(encrypted_filedata.encode())
                    # 更新下载进度
                    progress_bar(recv_size, file_size)
                else:
                    encrypted_filedata = clientServer.recv(file_size - recv_size).decode()
                    clientServer.send("yes".encode())
                    recv_size = file_size
                    f.write(encrypted_filedata.encode())
                    progress_bar(recv_size, file_size)
            # 接收加密后的key
            key_encrypted = int(clientServer.recv(MAXBUFFSIZE).decode())
            clientServer.send("yes".encode())
            # 接受加密后的iv
            iv_encrypted = int(clientServer.recv(MAXBUFFSIZE).decode())
            clientServer.send("yes".encode())
            # 接收客户端发来的源文件md5
            recv_digest = clientServer.recv(32).decode()
            clientServer.send("yes".encode())
            print("\nThe file is being decrypted, please wait...")
            decrypted_filepath, decrypted_path_digest = file_decrypt(encrypted_filepath, key_encrypted, iv_encrypted)
            if recv_digest != decrypted_path_digest:
                print("\n[Warning]: the file you received may be broken！")
                # 删除源文件和加密文件
                f.close()
                os.remove(decrypted_filepath)
                os.remove(decrypted_filepath + ".encrypted")
            else:
                end = time.time()
                print("\nGet the file successfully!")
                print("Spend time: " + str(int(end - start)) + "s")
                f.close()
                # 删除加密文件
                os.remove(decrypted_filepath + ".encrypted")

        else:
            print("[ERROR]: Can't find file")
    except:
        print("\n[Error]: Transfer failed")
        clientServer.close()
    print("*********************************************************************************************************")
    return 0


# 从服务端下载文件
def get_file_stream(filename):
    print("\n*********************************************************************************************************")
    print("Ready to transfer the file")
    start = time.time()
    """
    ...
    与服务端建立TCP连接
    ...
    """
    clientServer.settimeout(10000)
    filepath = CLIENT_WORKDIR + filename
    try:
        # 首先得到下载的文件大小(为了传输大文件,因此要分组接收)
        file_size = clientServer.recv(BUFFSIZE).decode()
        clientServer.send("yes".encode())
        file_size = int(file_size, 10)
        # 计算传输的次数
        count = (int(file_size) // BUFFSIZE_SENT) + 1
        if file_size > 0:
            f = open(filepath, 'wb')
            # 已接收的文件大小
            recv_size = 0
            print("Start transferring...")
            print("The file needs to be encrypted/decrypted, please wait...")
            # 循环接收文件
            while count:
                # 接收加密分组
                filedata_encrypted = clientServer.recv(BUFFSIZE).decode()
                clientServer.send("yes".encode())
                # 接收key
                key_encrypted = int(clientServer.recv(BUFFSIZE).decode())
                clientServer.send("yes".encode())
                # 接收iv
                iv_encrypted = int(clientServer.recv(BUFFSIZE).decode())
                clientServer.send("yes".encode())
                # 对分组进行解密
                filedata_decrypted = transfer_decrypt(filedata_encrypted, key_encrypted, iv_encrypted)
                f.write(b64decode(filedata_decrypted.encode()))
                # 更新下载进度
                recv_size += BUFFSIZE_SENT
                if recv_size > file_size:
                    recv_size = file_size
                progress_bar(recv_size, file_size)
                count -= 1
            f.close()
            # 接收原文件md5值
            recv_digest = clientServer.recv(32).decode()
            clientServer.send("yes".encode())
            if recv_digest != get_file_md5(filepath):
                print("\n[Warning]: The file you received may be broken！")
            else:
                end = time.time()
                print("\nGet the file successfully!")
                print("Spend time: " + str(int(end - start)) + "s")
        else:
            print("[ERROR]: Can't find file")
    except:
        print("\n[Error]: Transfer failed")
        clientServer.close()
    print("*********************************************************************************************************\n")
    return 0


def main():
    global client_e, client_n, client_d, server_e, server_n
    client_e, client_n = get_public_key(CLIENT_PUB_PATH)
    client_d = get_private_key(CLIENT_KEY_PATH)
    server_e, server_n = get_public_key(CLIENT_PUB_PATH)

    clientServer.connect(SERVER_ADDRESS)
    cmdinfo = clientServer.recv(BUFFSIZE).decode()
    while True:
        command = input(cmdinfo + "\n[+] ")
        while not command:
            command = input("[+] ")
        clientServer.send(command.encode('utf-8'))
        # 将消息按空格进行分割，比如command[0] = upload command[1] = filename
        command = command.split()
        if command[0] == "list" and len(command) == 1:
            recv_filelist()
        elif command[0] == "get1" and len(command) == 2:
            get_file_stream(command[1])
        elif command[0] == "get2" and len(command) == 2:
            get_file(command[1])

        elif command[0] == "exit" and len(command) == 1:
            clientServer.close()
            break

        else:
            print("Please input the correct command.")


if __name__ == '__main__':
    main()
    # a,b,c,d
