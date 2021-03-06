import pandas as pd
import math
from datetime import datetime

fips = pd.read_csv("fips/us-state-ansi-fips.csv")
mainDF = pd.read_excel("statePop.xlsx")

num = 24 + 21  # number of days with data

for i in range(num):
    label = "infected_day" + str(i)
    mainDF[label] = 0

R_0 = 2  # Basic reproduction ratio
incubationDur = 6.4  # Average incubation per
infectionDur = 7  # Average dur of infection
dt = 1  # Time step
peopleSeen = 13.7  # Avg number of people seen by average American

alpha = 1 - math.exp(-1 / incubationDur)  # Daily prob of individual becoming infectious
gamma = 1 - math.exp(-1 / infectionDur)  # Daily prob an individual recovers
beta = R_0 * gamma  # Scaled transmission rate


def numSus(t, pop):  # Susceptible to Exposed func
    infProb = I[t] * peopleSeen * pop / S[t]
    return infProb * dt  # How many people infected people have met with, weighted by population outdoors


def numInfected(t, modf):
    bound = 21 - modf * 6
    if (t < bound):
        asymp = .4  # (1-asymp) is prob of asympotomatic
    else:
        asymp = .8
    return (1 - asymp) * alpha * E[t] * dt  # daily prob of being infected after exposure * exposed pop


def numRecovery(t):
    return gamma * I[t] * dt  # daily prob that an individual recovers * number of infected people

"""
SEIR model for med-sized states (1,500,000 < pop < 10,000,000)
"""
def sGrowth(t, pop):  # Current pop (S[t]) - exposed
    return S[t] - numSus(t, pop)

def eGrowth(t, pop, modf):  # number of people who have been exposed (numSus) - number of people infected in last timestep
    return numSus(t, pop) - numInfected(t, modf)

def iGrowth(t, modf):  # Infected previously + newly infected - recovered + growth in actual infected cases
    return I[t] + numInfected(t, modf) - numRecovery(t)

def rGrowth(t):  # Recovered
    return R[t] + numRecovery(t)

"""
SEIR model for large states (pop > 10,000,000)
"""
def numInfectedLarge(t, modf):
    bound = 24 - modf * 3.5
    if t < bound:
        asymp = .4                           # (1-asymp) is prob of asympotomatic
    else:
        asymp = .8
    return (1-asymp) * alpha * E[t] * dt

def sGrowthLarge(t, pop): # Current pop (S[t]) - exposed
    return S[t] - numSus(t, pop)

def eGrowthLarge(t, pop, modf): # number of people who have been exposed (numSus) - number of people infected in last timestep
    return numSus(t, pop) - numInfectedLarge(t, modf)

def iGrowthLarge(t, modf): # Infected previously + newly infected - recovered + growth in actual infected cases
    return I[t] + numInfectedLarge(t, modf) - numRecovery(t)

def rGrowthLarge(t): # Recovered
    return R[t] + numRecovery(t)

"""
SEIR model for small states (pop < 1,500,000)
"""
def numInfectedSmall(t, modf):
    bound = 24 - modf * 2.5
    if (t < bound):
        asymp = .4                           # (1-asymp) is prob of asympotomatic
    else:
        asymp = .8
    return (1-asymp) * alpha * E[t] * dt

def sGrowthSmall(t, pop): # Current pop (S[t]) - exposed
    return S[t] - numSus(t, pop)

def eGrowthSmall(t, pop, modf): # number of people who have been exposed (numSus) - number of people infected in last timestep
    return numSus(t, pop) - numInfectedSmall(t, modf)

def iGrowthSmall(t, modf): # Infected previously + newly infected - recovered + growth in actual infected cases
    return I[t] + numInfectedSmall(t, modf) - numRecovery(t)

def rGrowthSmall(t): # Recovered
    return R[t] + numRecovery(t)


for i in range(mainDF.shape[0]):
    row = mainDF.iloc[i]

    stNameMod = row['State']
    stName = stNameMod[1:]  # Dataset has extra period
    stAbbrev = fips.loc[i]['stusps']
    stdataPath = "States_data/" + stAbbrev + "_data.xlsx"
    stData = pd.read_excel(stdataPath)

    S = [row['Population']]
    E = [0]
    I = [0]
    R = [0]
    timeIndex = 0
    firstCase = False

    for j in range(num):
        if j < 2:
            datePath = '3-0' + str(j + 8)
        elif 2 <= j < 24:
            datePath = '3-' + str(j + 8)
        elif 24 <= j < 33:
            datePath = '4-0' + str(j - 23)
        else:
            datePath = '4-' + str(j - 23)
        dateNow = datePath + '-2020'
        ourDate = datetime.strptime(dateNow, '%m-%d-%Y').date()

        if not firstCase:
            infectedNum = 0
            for x in range(timeIndex, stData.shape[0]):
                covidDate = stData['seconds_since_Epoch'].iloc[x]
                covidDate = datetime.fromtimestamp(covidDate).date()
                if ourDate == covidDate:
                    infectedNum = stData.iloc[j][2]
                    if not math.isnan(infectedNum) and int(infectedNum) != 0:
                        firstCase = True
                        I[j] += int(infectedNum)
                        break
                elif covidDate > ourDate:
                    timeIndex = x
                    break

        path = "data/data" + datePath + '.xlsx'
        data = pd.read_excel(path)
        percentAtHome = data.loc[j]['percentAtHome']
        atHome = .1 * percentAtHome / 100 * S[j]

        if mainDF.loc[i]['Population'] > 10000000:
            modf = mainDF.loc[i]['Population'] / 10000000
            S.append(sGrowthLarge(j, S[j] - atHome))
            E.append(eGrowthLarge(j, S[j] - atHome, modf))
            I.append(iGrowthLarge(j, modf))
            R.append(rGrowthLarge(j))
        elif mainDF.loc[i]['Population'] < 1500000:
            modf = (mainDF.loc[i]['Population'] / 200000)
            S.append(sGrowthSmall(j, S[j] - atHome))
            E.append(eGrowthSmall(j, S[j] - atHome, modf))
            I.append(iGrowthSmall(j, modf))
            R.append(rGrowthSmall(j))
        else:
            modf = (mainDF.loc[i]['Population'] / 8000000)
            S.append(sGrowth(j, S[j] - atHome))
            E.append(eGrowth(j, S[j] - atHome, modf))
            I.append(iGrowth(j, modf))
            R.append(rGrowth(j))

        label = "infected_day" + str(j)
        mainDF.at[i, label] = I[j]

    if i % 10 == 0:
        print(str(i / 50 * 100) + "% done")

finalPath = "final/finalDataMod.xlsx"
mainDF.to_excel(finalPath, sheet_name='main', index=False)
