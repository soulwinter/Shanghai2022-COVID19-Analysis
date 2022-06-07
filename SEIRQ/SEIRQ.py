import random
from math import floor
from pandas import DataFrame
import matplotlib.pyplot as plt

# 当发现疫情时，我们以一个防范区的范围为 S；即只考虑该防范区内的范围

# 以下是可以调整的参数
timeLength = 365  # 观测时长
# 病毒特性
R0 = 10  # 直接感染率
deathRate = 35/100000  # 死亡率
vaccineProtectionRate = 0.3  # 疫苗防护率
asymptomaticRate = 0.9  # 无症状比例
infectedAgainRate = 0.01
lengthOfIncubationPeriod = 10  # 潜伏期长度, FIXME: 下面改了
lengthOfTreatment = 14  # 治疗时间
asymptomaticToDiagnosedRate = 0.0005  # 每天无症状向确诊转变的概率，注意和 asymptomaticRate 的关系
# 政策措施
frequencyOfTesting = 3  # 核酸检测频率
useLockdown = True  # 发现病例时是否封控
fkProportion = 0.4  # 封控区占比
gkProportion = 0.4
ffProportion = 0.2  # 用上面两个减去，程序中没有用到
fkLeastTime = 7  # 连续多少天没病例就可以解除封控
vaccineRate = 0.7  # 疫苗接种比率
# 其他
Rfk = 0.05  # 封控区感染率是普通感染率的比重（实际感染率 R0 * Rfk， 下同)
Rgk = 0.5  # 管控区感染率
Rff = 0.7  # 防范区感染率
testValidityRate = 0.73  # 核酸检测有效率
lengthToHospital = 2  # 确诊患者从发病到去医院的时长

firstInfected = 5000  # 最开始的无症状感染者
totalHealthyPeople = 100000

# ----------------------------------------------------------------------------------------------------

# **以下初始化参数，请不要动**
S = [totalHealthyPeople] * (timeLength + lengthOfTreatment * 3)  # 易感人群【位于普通区，没打疫苗】
Sfk = [0] * (timeLength + lengthOfTreatment * 3)  # 封控区人数
Sgk = [0] * (timeLength + lengthOfTreatment * 3)  # 管控区人数
Sff = [0] * (timeLength + lengthOfTreatment * 3)  # 防范区人数
E = [0] * (timeLength + lengthOfTreatment * 3)  # 潜伏期人群
P = [0] * (timeLength + lengthOfTreatment * 3)  # 确诊患者
I = [0] * (timeLength + lengthOfTreatment * 3)  # 无症状患者
I[0] = firstInfected
R = [0] * (timeLength + lengthOfTreatment * 3)  # 康复人群（可能再次感染）
D = [0] * (timeLength + lengthOfTreatment * 3)  # 死亡人数
Q = [0] * (timeLength + lengthOfTreatment * 3)  # 隔离人群（居家隔离或方舱隔离）
Qh = [0] * (timeLength + lengthOfTreatment * 3)  # 医院隔离人数
getI = [0] * (timeLength + lengthOfTreatment * 3)  # 医疗机构获得的无症状数据
getP = [0] * (timeLength + lengthOfTreatment * 3)  # 医疗机构获得的确诊数据

testDate = 0  # 核酸检测时间是否到 核酸检测频率
toInfect = [0] * (timeLength + lengthOfTreatment * 3)
pToHospital = [0] * (timeLength + lengthOfTreatment * 3)
hospitalToR = [0] * (timeLength + lengthOfTreatment * 3)
qhToR = [0] * (timeLength + lengthOfTreatment * 3)
qhToD = [0] * (timeLength + lengthOfTreatment * 3)
qtoR = [0] * (timeLength + lengthOfTreatment * 3)
noCasesDays = 0
inLockdown = False

for i in range(1, timeLength + 1):
    # 初始化数据
    testDate += 1
    totalInitReinfected = random.randint(0, floor(R[i-1] * infectedAgainRate * 2))
    lengthOfIncubationPeriod = random.randint(3, 18)

    S[i] = S[i - 1]  # S 为所有可能感染的人群数量
    Sfk[i] = Sfk[i - 1]
    Sgk[i] = Sgk[i - 1]
    Sff[i] = Sff[i - 1]
    E[i] = E[i - 1]
    I[i] = I[i - 1]
    P[i] = P[i - 1]
    Q[i] = Q[i - 1]
    Qh[i] = Qh[i - 1]
    R[i] = R[i - 1]
    D[i] = D[i - 1]
    totalS = S[i] + Sgk[i] + Sfk[i] + Sff[i] + totalInitReinfected  # 所有可以被感染的人数

    # 首先是感染进入潜伏期
    totalInitInfected = floor((P[i] + I[i]) * R0 * (1 - vaccineProtectionRate) * (1 - vaccineRate))  # 如果没有任何措施，会感染的人数
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
        toInfect[
            i + lengthOfIncubationPeriod] += peopleInfectedFF + peopleInfectedGK + peopleInfectedFK + peopleInfectedNormal  # 在 i + lengthOfIncubationPeriod 需要转入确诊的人数
        Sfk[i] -= peopleInfectedFK
        Sgk[i] -= peopleInfectedGK
        Sff[i] -= peopleInfectedFF
        S[i] -= peopleInfectedNormal

        # 考虑再次感染
        if totalInitReinfected > 0:
            if inLockdown:
                # 治愈者在封控区：
                tempReinfected = floor(totalInitInfected * totalInitReinfected * fkProportion / totalS * Rfk)
                if tempReinfected > floor(totalInitReinfected * fkProportion):
                    tempReinfected = floor(totalInitReinfected * fkProportion)
                toInfect[i+lengthOfIncubationPeriod] += tempReinfected
                E[i] += tempReinfected
                R[i] -= tempReinfected
                # 治愈者在管控区
                tempReinfected = floor(totalInitInfected * totalInitReinfected * gkProportion / totalS * Rgk)
                if tempReinfected > floor(totalInitReinfected * gkProportion):
                    tempReinfected = floor(totalInitReinfected * gkProportion)
                toInfect[i + lengthOfIncubationPeriod] += tempReinfected
                E[i] += tempReinfected
                R[i] -= tempReinfected
                # 治愈者在防范区
                tempReinfected = floor(totalInitInfected * totalInitReinfected * ffProportion / totalS * Rff)
                if tempReinfected > floor(totalInitReinfected * ffProportion):
                    tempReinfected = floor(totalInitReinfected * ffProportion)
                toInfect[i + lengthOfIncubationPeriod] += tempReinfected
                E[i] += tempReinfected
                R[i] -= tempReinfected
            else:
                tempReinfected = floor(totalInitInfected * totalInitReinfected / totalS)
                if tempReinfected > floor(totalInitReinfected * ffProportion):
                    tempReinfected = floor(totalInitReinfected * ffProportion)
                toInfect[i + lengthOfIncubationPeriod] += tempReinfected
                E[i] += tempReinfected
                R[i] -= tempReinfected

    # 无症状向确诊转变
    if floor(I[i] * asymptomaticToDiagnosedRate) > 0:
        P[i] += floor(I[i] * asymptomaticToDiagnosedRate)
        I[i] -= floor(I[i] * asymptomaticToDiagnosedRate)
        pToHospital[i + (lengthToHospital if not inLockdown else random.randint(1, 2))] += floor(I[i] * asymptomaticToDiagnosedRate)
        # 封控时间 患者会更快去医院，不受核酸结果有效率影响

    # 潜伏期转入确诊或无症状
    if toInfect[i] > 0:
        I[i] += floor(toInfect[i] * asymptomaticRate)
        P[i] += toInfect[i] - floor(toInfect[i] * asymptomaticRate)
        E[i] -= toInfect[i]
        pToHospital[i + (lengthToHospital if not inLockdown else random.randint(0, 2))] += toInfect[i] - floor(toInfect[i] * asymptomaticRate)

    print("------------------------------------------------------")
    print(i, "可感染人数:", S[i] + Sfk[i] + Sgk[i] + Sff[i], "确诊病例:", P[i], "无症状：", I[i], "潜伏期：", E[i], "医院人数：", Qh[i],
          "方舱医院人数：", Q[i], "治愈：", R[i], "死亡：", D[i])

    # 确诊病例去医院
    if pToHospital[i] > 0:
        Qh[i] += pToHospital[i]
        P[i] -= pToHospital[i]
        qhToD[i + random.randint(1, lengthOfTreatment)] += floor(pToHospital[i] * deathRate)
        qhToR[i + lengthOfTreatment] += pToHospital[i] - floor(pToHospital[i] * deathRate)
        getP[i] += pToHospital[i]  # 医疗机构获得
        print("第", i, "天: 新增确诊病例", pToHospital[i], "例.")
        # TODO: 政策响应
        if not inLockdown and useLockdown:
            print("开始封控")
            inLockdown = True
            Sfk[i] = floor(S[i] * fkProportion)
            Sgk[i] = floor(S[i] * gkProportion)
            Sff[i] = S[i] - Sfk[i] - Sgk[i]
            S[i] = 0

    if qhToD[i] > 0:
        Qh[i] -= qhToD[i]
        D[i] += qhToD[i]
        print("第", i, "天: 新增死亡病例", round(qhToD[i]), "例.")

    if qhToR[i] > 0:
        Qh[i] -= qhToR[i]
        R[i] += qhToR[i]
        print("第", i, "天: 治愈确诊病例", round(qhToR[i]), "例.")

    if qtoR[i] > 0:
        Q[i] -= qtoR[i]
        R[i] += qtoR[i]
        print("第", i, "天: 无症状感染者解除隔离", round(qtoR[i]), "例.")

    # 全域规模的核酸检测
    if testDate % frequencyOfTesting == 0 or inLockdown:
        # getPositive = 0
        # for j in range(0, I[i]):
        #     if random.random() < testValidityRate:
        #         getPositive += 1
        getPositive = floor(I[i] * testValidityRate)
        if getPositive == I[i] - 1:
            temp = random.random()
            if temp < testValidityRate:
                getPositive += 1

        I[i] -= getPositive
        Q[i] += getPositive
        qtoR[i + lengthOfTreatment] += getPositive

        if inLockdown and getPositive == 0:
            noCasesDays += 1
            if noCasesDays >= fkLeastTime:
                inLockdown = False
                S[i] = Sgk[i] + Sfk[i] + Sff[i]
                Sgk[i] = 0
                Sfk[i] = 0
                Sff[i] = 0
                noCasesDays = 0

        if inLockdown and getPositive != 0:
            noCasesDays = 0

        if round(getPositive) > 0 or inLockdown:
            print("第", i, "天: 在全域核酸检测中，发现无症状感染者", round(getPositive), "例.")
            getI[i] += getPositive  # 医疗机构获得

        if not inLockdown and getPositive > 0 and useLockdown:
            print("开始封控")
            inLockdown = True
            Sfk[i] = floor(S[i] * fkProportion)
            Sgk[i] = floor(S[i] * gkProportion)
            Sff[i] = S[i] - Sfk[i] - Sgk[i]
            S[i] = 0

# ----------------------------------------------------------------------------------------------------

data = {
    "实际确诊人数": P,
    "实际无症状人数": I,  # 请注意，每天实际的无症状是减去了当日发现的病例的
    "检测确诊人数": getP,
    "检测无症状人数": getI,
    "医院人数": Qh,
    "方舱医院人数": Q,
    "康复人数": R,
    "死亡人数": D,
    "未感染普通区人数": S,
    "未感染封控区人数": Sfk,
    "未感染管控区人数": Sgk,
    "未感染防范区人数": Sff
}
# dataFrame 即最后返回结果，包含以上信息
dataFrame = DataFrame(data)
dataFrame[:timeLength].to_csv("result.csv")  # 保存 .csv 文件

# 绘图，下图是一个简单样例，不是最终版本
dayPlot = timeLength

plt.plot(range(dayPlot), Qh[0:dayPlot], color="r")
plt.plot(range(dayPlot), Q[0:dayPlot], color="grey")
plt.show()
