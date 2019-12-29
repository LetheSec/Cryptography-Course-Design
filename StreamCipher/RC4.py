import base64


def get_sbox(k):
    # 将0~255装入S盒
    sBox = list(range(256))
    T = [ord(k[i % len(k)]) for i in range(256)]
    # 根据密钥打乱S盒
    j = 0
    for i in range(256):
        j = (j + sBox[i] + T[i]) % 256
        sBox[i], sBox[j] = sBox[j], sBox[i]
    return sBox


def prga(m, key):
    res = ''
    i = j = 0
    s = get_sbox(key)
    for n in m:
        i = (i + 1) % 256
        j = (j + s[i]) % 256
        s[i], s[j] = s[j], s[i]
        t = (s[i] + s[j]) % 256
        k = s[t]
        res += chr(ord(n) ^ k)
    return res


def encrypt(message, key):
    return base64.b64encode(prga(message, key).encode()).decode()


def decrypt(cipher, key):
    return prga(base64.b64decode(cipher).decode(), key)


def main():
    while True:
        mode = input("请选择模式:\n[E]加密\t[D]解密\t[Q]退出\n")
        if mode == 'E' or mode == 'e':
            message = input("请输入明文:\n")
            key = input("请输入密钥:\n")
            cipher = encrypt(message, key)
            print("密文为:\n" + cipher)
        elif mode == 'D' or mode == 'd':
            cipher = input("请输入密文:\n")
            key = input("请输入密钥:\n")
            message = decrypt(cipher, key)
            print("明文为:\n" + message)
        elif mode == 'Q' or mode == 'q':
            break
        else:
            continue


if __name__ == '__main__':
    import time
    message = 'IamYXJ.'
    key = 'cumt1234'
    start = time.time()
    for i in range(10000):
        cipher = encrypt(message, key)
    end = time.time()
    print("encrypt spend time: " + str(end - start) + " seconds.")
    start = time.time()
    for i in range(10000):
        message = decrypt(cipher, key)
    end = time.time()
    print("decrypt spend time: " + str(end - start) + " seconds.")
