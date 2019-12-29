# 20次本原多项式:x^20 + x^8 + x^6 + x^5 + x^2 + x^1 + 1
# 5 3 2 1
# 10 4 3 1
def feedback(reg, fb):
    """
    反馈函数
    :param reg: 移位寄存器的内容
    :param fb: 由抽头构成的列表
    :return: 最左端的输入
    """
    res = reg[fb[0] - 1]
    for i in range(1, len(fb)):
        res = int(res) ^ int(reg[fb[i] - 1])
    return res


def lfsr(p):
    """
    线性反馈移位寄存器
    :param p: 由本原多项式次数构成的列表
    :return:
    """
    reg_len = max(p)
    # 初始寄存器状态:00000....001
    shift_reg = '1'.zfill(reg_len)
    regs = [shift_reg]  # 存放寄存器的各个状态
    output_ = []  # 存放输出序列
    for i in range(pow(2, reg_len) - 1):
        # 输出寄存器最右端的值
        output_.append(shift_reg[-1])
        # 计算抽头异或的值
        input_ = str(feedback(shift_reg, p))
        shift_reg = input_ + shift_reg[:-1]
        # 如果寄存器当前状态已经出现过了,说明一个周期结束
        if shift_reg in regs:
            break
        else:
            regs.append(shift_reg)
    return output_, regs


def main():
    while True:
        try:
            ct = input("\n请输入本原多项式x的系数(以空格分隔):\n").split(" ")
            if ('q' in ct) or ('Q' in ct):
                break
            ct = [int(ct[i]) for i in range(len(ct))]
            print("您输入的本原多项式为:")
            for i in range(len(ct)):
                print("x^" + str(ct[i]) + " + ", end="")
            print("1")
            print("理论最大周期为: " + str(pow(2, max(ct)) - 1))
            mode = input("是否确认:\n[Y]确定\t[N]重新输入\t[Q]退出\n")
            if mode == 'Y' or mode == 'y':
                outputs, regs = lfsr(ct)
                print("\n周期为: " + str(len(outputs)))
                choice1 = input("是否查看输出序列:\n[Y]是\t[N]否\n")
                if choice1 == 'Y' or choice1 == 'y':
                    for i in outputs:
                        print(i, end="")
                choice2 = input("\n是否输出周期内寄存器各状态:\n[Y]是\t[N]否\n")
                if choice2 == 'Y' or choice2 == 'y':
                    with open('regs.txt', 'w') as f:
                        for i in regs:
                            f.write(i + "\n")
                    print("成功！周期内寄存器各状态保存在regs.txt")
            elif mode == 'N' or mode == 'n':
                continue
            else:
                if mode == 'Q' or mode == 'q':
                    break
                else:
                    continue
        except:
            print("输入有误!")
            continue


if __name__ == '__main__':
    main()
