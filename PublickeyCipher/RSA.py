from random import randint
#from libnum import *
import libnum
import sys
import time

# 设置最大递归深度,否则在fast_mod中可能会报错
sys.setrecursionlimit(2147483647)


def extended_gcd(a, b):
    """
    扩展的欧几里得算法计算gcd的最大公因子g以及x和y,满足g=ax+by
    递归式的推导过程:
    ax₁ + by₁ = gcd(a,b)
    bx₂ + (a%b)y₂ = gcd(b,a%b)
    ∵ gcd(a,b) = gcd(b,a%b) 且 a%b = a - (a//b)*b
    ∴ bx₂ + (a%b)y₂
     = bx₂ + [a - (a//b)*b]y₂
     = ay₂ + bx₂ - (a//b)by₂
     = ay₂ + b[x₂ - (a//b)y₂]
     = ax₁ + by₁
     ∴待定系数法得:x₁ = y₂, y₁ = x₂ - (a//b)y₂
     递归终止条件: 当b = 0, gcd(a,b) = a, 此时 x = 1,y = 0
    :return: (g,s,t)
    """
    if b == 0:
        return a, 1, 0
    else:
        g, x, y = extended_gcd(b, a % b)  # 先得到更里层的x₂,y₂,
        return g, y, x - (a // b) * y  # 再根据得到的x₂,y₂,计算x₁,y₁


def mod_inverse(a, m):
    """
    计算模逆,即a**-1 (mod m)
    :param a: 底数
    :param m: 模数
    :return: 逆元
    """
    g, x, y = extended_gcd(a, m)  # ax + my = 1
    # 若a,m不互素,则不可逆
    if g != 1:
        raise Exception(str(a) + ' is not invertible!')
    else:
        return x % m


def fast_mod(x, n, p):
    x = x % p
    res = 1
    while n!=0:
        if n & 1:
            res = (res * x) % p
        n >>= 1     # 相当于 n //= 2
        x = (x * x) % p
    return res

# import time
# start = time.time()
# for i in range(1000):
#     res = pow(1231, 12353534523412421, 21341311)
# end = time.time()
# print(res)
# print(end - start)
#
# print("fast mod")
# start = time.time()
# for i in range(1000):
#     res = fast_mod(1231, 12353534523412421, 21341311)
# end = time.time()
# print(res)
# print(end - start)


# from math import *
# def p(k,t):
#     return pow(k,3/2)*pow(2,t)*pow(t,-1/2)*pow(4,2-sqrt(t*k))
# for t in range(1,16):
#     print(str(t) + ": " + str(p(512, t)))


def miller_rabin(n, k=10):
    """
    用Miler-Rabin算法进行素性检验
    :param n: 被检验的数
    :param k: 检验的次数，默认为15次
    :return: 是否通过检验
    要测试n是否为素数,首先将n−1分解为(2^s)d
    在每次测试开始时,先随机选一个介于[1,n−1]的整数a,之后如果对所有的r∈[0,s−1] ,
    若a^d ≠1  (mod n)且 a^(2^rd)≠−1(mod n),则n是合数
    否则，n 有 3/4 的概率为素数,增加测试的次数,该数是素数的概率会越来越高。
    """
    # 偶数直接不通过
    if n % 2 == 0:
        return False
    s, d = 0, n - 1
    # 将p-1分解为(2**s)d
    while d % 2 == 0:
        s += 1
        d //= 2
    # 进行k次检验566++3.+6
    for i in range(k):
        # 每次测试时,随机选取一个[1,n-1]的整数a
        a = randint(1, n - 1)
        x = pow(a, d, n)  # x = a**d mod(n)
        # 如果a**d(mod n)=1,说明当次检验通过(不是合数),进行下一轮检验
        if x == 1 or x == n - 1:
            continue
        else:
            flag = 0
            # 对所有的r∈[0, s-1],判断a**((2**r)*d) (mod n)是否等于-1，
            for r in range(s):
                # x**pow(2,r) == a**d**pow(2,r)
                x = pow(x, 2, n)
                if x == n - 1:
                    flag = 1
                    break
            # 若a**d≠1(mod n)且a**pow(2,r)**≠
            if flag == 0:
                return False
    return True


def get_prime(n):
    """
    得到一个n位的素数(10进制表示)
    :param n: 二进制位数
    :return: n位素数(10进制表示)
    """
    while True:
        # 最高位为1,保证是n位
        num = '1'
        # 随机生成n-2位数
        for i in range(n - 2):
            x = randint(0, 1)
            num += str(x)
        # 最低位位1,保证是奇数
        num += '1'
        # 转为10进制
        num = int(num, 2)
        if miller_rabin(num):
            return num


def get_keys(nbits):
    """
    :param nbits: 密钥长度(512/1024/2048...)
    :return: 公钥(e,n),私钥d
    """
    nbits = int(nbits)
    while True:
        p = get_prime(nbits)
        # print("p: " + str(p))
        q = get_prime(nbits)
        #print("q: " + str(q))
        # 保证p != q
        if p == q:
            continue

        N = p * q
        phiN = (p - 1) * (q - 1)
        e = randint(500, 10000)
        # 保证e与phiN互素
        if extended_gcd(e, phiN)[0] == 1:
            # 计算私钥
            # print("p: " + str(p))
            # print("q: " + str(q))
            d = mod_inverse(e, phiN)
            return e, N, d


def Encrypt(m, e, n):
    e = int(e)
    n = int(n)
    c = pow(m, e, n)
    return c



def Decrypto(c, d, n):
    d = int(d)
    n = int(n)
    m = pow(c, d, n)
    return m


def main():
    while True:
        mode = input("\n请选择模式:\n[E]加密\t[D]解密\n")
        if mode == 'E' or mode == 'e':
            m = input("请输入明文:\n")
            nbits = input("请输入位数:\n")
            e, n, d = get_keys(nbits)
            print("公钥e为: " + str(e))
            print("公钥n为: " + str(n))
            print("私钥d为: " + str(d))
            print("明文为: " + m)
            m = libnum.s2n(m)
            # print(m)
            c = Encrypt(m, e, n)
            print("密文为(10进制): " + str(c))
        elif mode == 'D' or mode == 'd':
            c = input("请输入密文(10进制):\n")
            d = input("请输入私钥d:\n")
            n = input("请输入公钥n:\n")
            c = Decrypto(int(c), d, n)
            c = libnum.n2s(c)
            print("密文为: " + str(c))
        else:
            continue


if __name__ == '__main__':
    main()

