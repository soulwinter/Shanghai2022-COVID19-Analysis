import random
from math import floor

timeLength = 400
# 当发现疫情时，我们以一个防范区的范围为 S；即只考虑该防范区内的范围
# TODO: 进入机制，因外地传入【考虑做核酸后直接放行】，发现病例时，需要做多次核酸检测
# TODO: 康复概率
# TODO: 随机机制

S = [25000000] * timeLength  # 易感人群【位于普通区，没打疫苗】
Sfk = [0] * timeLength  # 封控区人数
Sgk = [0] * timeLength  # 管控区人数
Sff = [0] * timeLength  # 防范区人数
E = [0] * timeLength  # 潜伏期人群
P = [0] * timeLength  # 确诊患者
I = [0] * timeLength  # 无症状患者
R = [0] * timeLength  # 康复人群（可能再次感染） TODO: 考虑怎么解决这件事，当前设定是不会再次感染
D = [0] * timeLength  # 死亡人数
Q = [0] * timeLength  # 隔离人群（居家隔离或方舱隔离）
Qh = [0] * timeLength  # 医院隔离人数

# 以下是可以调整的参数
R0 = 8  # 直接感染率
Rnormal = 5  # 防疫措施感染率
Rfk = 0.05  # 封控区感染率（R * Rfk， 下同)
Rjj = 0.2  # 居家隔离感染率（应该等于封控区）
Rgk = 0.5  # 管控区感染率
Rff = 0.7  # 防范区感染率

fkProportion = 0.5  # 封控区占比
gkProportion = 0.2
ffProportion = 0.3  # 用上面两个减去，程序中没有用到
fkLeastTime = 7  # 连续多少天没病例就可以解除封控

vaccineProtectionRate = 0.4  # 疫苗防护率
vaccineRate = 0.7  # 疫苗接种比率
asymptomaticRate = 0.9  # 无症状比例
testValidityRate = 0.73  # 核酸检测有效率
InfectedAgainRate = 0.1  # 再次被感染的概率

lengthOfIncubationPeriod = 10  # 潜伏期长度
lengthToHospital = 2  # 确诊患者从发病到去医院的时长
frequencyOfTesting = 5  # 核酸检测频率
lengthOfTreatment = 14  # 治疗时间

# 初始化参数
testDate = 0  # 核酸检测时间是否到 核酸检测频率
toInfect = [0] * timeLength
pToHospital = [0] * timeLength
hospitalToR = [0] * timeLength
qhToR = [0] * timeLength
I[0] = 10000
noCasesDays = 0
startLockdown = False
# 模拟一年的动态清零
for i in range(1, 365 + 1):
    # 初始化数据
    testDate += 1
    lengthOfIncubationPeriod = random.randint(3, 15)

    S[i] = S[i - 1]  # S 为所有可能感染的人群数量
    Sfk[i] = Sfk[i - 1]
    Sgk[i] = Sgk[i - 1]
    Sff[i] = Sff[i - 1]
    E[i] = E[i - 1]
    totalS = S[i] + Sgk[i] + Sfk[i] + Sff[i]
    I[i] = I[i - 1]
    P[i] = P[i - 1]
    Q[i] = Q[i-1]
    Qh[i] = Qh[i-1]

    # 首先是感染进入潜伏期
    totalInitInfected = floor((P[i - 1] + I[i - 1]) * R0 * (1-vaccineProtectionRate) * (1-vaccineRate))  # 如果没有任何措施，会感染的人数
    if totalS > 0:
        peopleInfectedFK = floor(totalInitInfected * Sfk[i] / totalS * Rfk)
        if peopleInfectedFK > Sfk[i]:
            peopleInfectedFK = Sfk[i]
        peopleInfectedGK = floor(totalInitInfected * Sgk[i] / totalS * Rgk)
        if peopleInfectedGK > Sgk[i]:
            peopleInfectedGK = Sgk[i]
        peopleInfectedFF = floor(totalInitInfected * Sff[i] / totalS * Rff)
        if peopleInfectedFF > Sff[i]:
            peopleInfectedFF = Sff[i]
        peopleInfectedNormal = floor(totalInitInfected * S[i] / totalS)
        if peopleInfectedNormal > S[i]:
            peopleInfectedNormal = S[i]
        E[i] += peopleInfectedFF + peopleInfectedGK + peopleInfectedFK + peopleInfectedNormal
        toInfect[i + lengthOfIncubationPeriod] += peopleInfectedFF + peopleInfectedGK + peopleInfectedFK + peopleInfectedNormal  # 在 i + lengthOfIncubationPeriod 需要转入确诊的人数
        Sfk[i] -= peopleInfectedFK
        Sgk[i] -= peopleInfectedGK
        Sff[i] -= peopleInfectedFF
        S[i] -= peopleInfectedNormal



    # 潜伏期转入确诊或无症状
    if toInfect[i] > 0:
        I[i] += floor(toInfect[i] * asymptomaticRate)
        P[i] += toInfect[i] - floor(toInfect[i] * asymptomaticRate)
        E[i] -= toInfect[i]
        pToHospital[i + lengthToHospital] += toInfect[i] - floor(toInfect[i] * asymptomaticRate)

    print("------------------------------------------------------")
    print(i, "可感染人数:", S[i] + Sfk[i] + Sgk[i] + Sff[i], "确诊病例:", P[i], "无症状：", I[i], "潜伏期：", E[i], "医院人数：", Qh[i], "方舱医院人数：", Q[i])

    # 确诊病例去医院
    if pToHospital[i] > 0:
        Qh[i] += pToHospital[i]
        P[i] -= pToHospital[i]
        qhToR[i + lengthOfTreatment] += pToHospital[i]
        print("第", i, "天: 新增确诊病例", pToHospital[i], "例.")
        # TODO: 政策响应
        if not startLockdown:
            print("开始封控")
            startLockdown = True
            Sfk[i] = floor(S[i] * fkProportion)
            Sgk[i] = floor(S[i] * gkProportion)
            Sff[i] = S[i] - Sfk[i] - Sgk[i]
            S[i] = 0


    if qhToR[i] > 0:
        Qh[i] -= qhToR[i]
        R[i] += qhToR[i]
        print("第", i, "天: 治愈确诊病例", round(qhToR[i]), "例.")

    # 全域规模的核酸检测
    if testDate % frequencyOfTesting == 0 or startLockdown:
        getPositive = 0
        for j in range(0, I[i]):
            if random.random() < testValidityRate:
                getPositive += 1

        I[i] -= getPositive
        Q[i] += getPositive

        if startLockdown and getPositive == 0:
            noCasesDays += 1
            if noCasesDays >= fkLeastTime:
                startLockdown = False
                S[i] = Sgk[i] + Sfk[i] + Sff[i]
                Sgk[i] = 0
                Sfk[i] = 0
                Sff[i] = 0
                noCasesDays = 0
                print("封控解除!")

        if startLockdown and getPositive != 0:
            noCasesDays = 0

        if round(getPositive) > 0 or startLockdown:
            print("第", i, "天: 在全域核酸检测中，发现无症状感染者", round(getPositive), "例.")

        if not startLockdown and getPositive > 0:
            print("开始封控")
            startLockdown = True
            Sfk[i] = floor(S[i] * fkProportion)
            Sgk[i] = floor(S[i] * gkProportion)
            Sff[i] = S[i] - Sfk[i] - Sgk[i]
            S[i] = 0


