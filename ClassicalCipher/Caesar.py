def Encrypt(m, k):
    """
    凯撒密码加密
    :param m: 明文
    :param k: 密钥(移位量)
    :return: 加密的结果
    """
    k %= 26
    c = ''
    mlen = len(m)
    for i in range(mlen):
        if m[i].isupper():
            c += chr((ord(m[i]) - ord('A') + k) % 26 + ord('A'))
        elif m[i].islower():
            c += chr((ord(m[i]) - ord('a') + k) % 26 + ord('a'))
        else:
            c += m[i]
    return c


def Decrypt(c, k):
    """
    凯撒密码解密
    :param c: 密文
    :param k: 密钥
    :return: 解密的结果
    """
    k %= 26
    m = ''
    clen = len(c)
    for i in range(clen):
        if c[i].isupper():
            m += chr((ord(c[i]) - ord('A') - k + 26) % 26 + ord('A'))
        elif c[i].islower():
            m += chr((ord(c[i]) - ord('a') - k + 26) % 26 + ord('a'))
        else:
            m += c[i]
    return m


def Crack(c):
    for i in range(1, 26):
        print("k = " + str(i).zfill(2) + ": ", Decrypt(c, i))


def main():
    while True:
        mood = input("\nPlease choose a mood:\n[E]Encrypt\t[D]Decrypt\t[C]Crack\t[Q]Quit\n")
        if mood == 'E' or mood == 'e':
            message = input("Please input the message:\n")
            key = input("Please input the key:\n")
            cipher = Encrypt(message, int(key))
            print("The cipher is:\n" + cipher)
        elif mood == 'D' or mood == 'd':
            cipher = input("Please input the cipher:\n")
            key = input("Please input the key:\n")
            message = Decrypt(cipher, int(key))
            print("The message is:\n" + message)
        elif mood == 'C' or mood == 'c':
            cipher = input("Please input the cipher:\n")
            print("Possible messages:\n")
            Crack(cipher)
        elif mood == 'Q' or mood == 'q':
            break
        else:
            continue


if __name__ == '__main__':
    main()
