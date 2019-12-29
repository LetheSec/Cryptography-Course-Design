def Encrypt(m, k):
    """
    维吉尼亚密码加密
    :param m: 明文
    :param k: 密钥
    :return: 密文
    """
    c = ''
    j = 0
    for i in range(len(m)):
        if m[i].isupper():
            c += chr(((str2num(m[i]) + str2num(k[j % len(k)])) % 26) + ord('A'))
            j += 1
        elif m[i].islower():
            c += chr(((str2num(m[i]) + str2num(k[j % len(k)])) % 26 + ord('a')))
            j += 1
        else:
            c += m[i]
    return c


def Decrypt(c, k):
    """
    维吉尼亚密码解密
    :param c: 密文
    :param k: 密钥
    :return: 明文
    """
    m = ''
    j = 0
    for i in range(len(c)):
        if c[i].isupper():
            m += chr(((str2num(c[i]) - str2num(k[j % len(k)]) + 26) % 26) + ord('A'))
            j += 1
        elif c[i].islower():
            m += chr(((str2num(c[i]) - str2num(k[j % len(k)]) + 26) % 26) + ord('a'))
            j += 1
        else:
            m += c[i]
    return m


def Crack(c):
    """
    唯密文攻击破解密钥
    :param c: 密文
    :return: 密钥
    """
    cipher = ''
    c = c.lower()
    # 删除特殊符号
    for ch in c:
        if ch.islower():
            cipher += ch
    keylength = get_keyLength(cipher)
    key = get_key(cipher, keylength)
    return key


# 获取密钥长度
# 遍历3-20位,相同间隔的字母相同数最多的位数,即最有可能为密钥长度
def get_keyLength(cipher):
    keyLen = 1
    maxCount = 0
    # 密钥长度3-20位
    for step in range(3, 21):
        count = 0
        for i in range(len(cipher) - step):
            if cipher[i] == cipher[i - step]:
                count += 1
        if count > maxCount:
            maxCount = count
            keyLen = step
    return keyLen


# 确定密钥
def get_key(text, length):
    key = ''
    alphaFreq = [0.082, 0.015, 0.028, 0.043, 0.127, 0.022, 0.02, 0.061, 0.07, 0.002, 0.008, 0.04, 0.024,
                 0.067, 0.075, 0.019, 0.001, 0.06, 0.063, 0.091, 0.028, 0.01, 0.023, 0.001, 0.02, 0.001]
    # 将密文分组
    cipher_matrix = cipherSplit(text, length)
    # 逐个字母猜解
    for i in range(length):
        # 获取每组密文中用同一字母加密的(即二维矩阵中的一列)
        col = [row[i] for row in cipher_matrix]
        # 计算该分组里的字母频率
        freq = countFreq(col)
        IC = []  # 存放26种情况的重合指数
        for j in range(26):
            ic = 0.00000
            # 计算IC = 累和(Ni/L * fi)
            for k in range(26):
                ic += freq[k] * alphaFreq[k]
            IC.append(ic)
            # 如果一个分组用b加密，a的频率会转移到b上、c转移到d上...
            # 我们也做这种相应的转移，让b字符在密文的频率（N1/L）和a字符在英文的频率f0相乘
            # 若猜测正确那么ic应该最接近0.067
            freq = freq[1:] + freq[:1]  # 循环左移1位
        temp = 1
        ch = ''
        # 找出最接近重合指数的那一个字母
        for j in range(len(IC)):
            if abs(IC[j] - 0.065546) < temp:
                temp = abs(IC[j] - 0.065546)  # 保存当前最接近的差值
                ch = chr(j + 97)  # 转换为字母
        key += ch
    return key


# 统计a-z字母出现的频率
def countFreq(text):
    freq = []
    for i in range(97, 123):
        count = 0
        for ch in text:
            if ch == chr(i):
                count += 1
        freq.append(count / len(text))
    return freq


# 根据密钥长度对密文分组,用二维矩阵表示
# 每一行都是用按密钥加密,每一列都是用同一个字母移位加密的
def cipherSplit(text, length):
    cipher_matrix = []  # 二维矩阵
    row = []  # 每一行都是按密钥加密的,长度为密钥长度
    i = 0
    for ch in text:
        row.append(ch)
        i += 1
        if i % length == 0:
            cipher_matrix.append(row)
            row = []
    return cipher_matrix


# 将字母转换为数字
def str2num(s):
    if s.isupper():
        return (ord(s) - ord('A')) % 26
    elif s.islower():
        return (ord(s) - ord('a')) % 26


def main():
    while True:
        mode = input("\nPlease choose a mode:\n[E]Encrypt\t[D]Decrypt\t[C]Crack\t[Q]Quit\n")
        # 加密
        if mode == 'E' or mode == 'e':
            try:
                message = input("Please input the message:\n")
                key = input("Please input the key:\n")
                cipher = Encrypt(message, key)
                print("The cipher is:\n" + cipher)
            except:
                print("Something Wrong!")
        # 解密
        elif mode == 'D' or mode == 'd':
            try:
                cipher = input("Please input the cipher:\n")
                key = input("Please input the key:\n")
                message = Decrypt(cipher, key)
                print("The message is:\n" + message)
            except:
                print("Something Wrong!")
        # 唯密文攻击
        elif mode == 'C' or mode == 'c':
            try:
                cipher = input("Please input the cipher:\n")
                key = Crack(cipher)  # 唯密文攻击获取密钥
                print("The key might be:\n" + key)
                message = Decrypt(cipher, key)  # 用获取的密钥进行解密
                print("The message might be:\n" + message)
            except:
                print("Something Wrong!")
        # 退出
        elif mode == 'Q' or mode == 'q':
            break
        else:
            continue


if __name__ == '__main__':
    main()
