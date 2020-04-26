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
peopleSeen = 10  # Avg number of people seen by average American

alpha = 1 - math.exp(-1 / incubationDur)  # Daily prob of individual becoming infectious
gamma = 1 - math.exp(-1 / infectionDur)  # Daily prob an individual recovers
beta = R_0 * gamma  # Scaled transmission rate


def numSus(t, pop):  # Susceptible to Exposed func
    infProb = I[t] * peopleSeen * pop / S[t]
    return infProb * dt  # How many people infected people have met with, weighted by population outdoors


def numInfected(t):
    if (t < 28):
        asymp = .4  # (1-asymp) is prob of asympotomatic
    else:
        asymp = .8
    return (1 - asymp) * alpha * E[t] * dt  # daily prob of being infected after exposure * exposed pop


def numRecovery(t):
    return gamma * I[t] * dt  # daily prob that an individual recovers * number of infected people


def sGrowth(t, pop):  # Current pop (S[t]) - exposed
    return S[t] - numSus(t, pop)


def eGrowth(t, pop):  # number of people who have been exposed (numSus) - number of people infected in last timestep
    return numSus(t, pop) - numInfected(t)


def iGrowth(t):  # Infected previously + newly infected - recovered + growth in actual infected cases
    return I[t] + numInfected(t) - numRecovery(t)


def rGrowth(t):  # Recovered
    return R[t] + numRecovery(t)


for i in range(5):
    row = mainDF.iloc[i]

    stNameMod = row['State']
    stName = stNameMod[1:]  # Dataset has extra period
    #stAbbrev = fips.loc[fips['stname'] == stName]['stusps'][i]
    stAbbrev = fips.loc[i]['stusps']
    print(stName, stAbbrev)
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
                covidDate = stData['seconds_since_Epoch'].iloc[j]
                covidDate = datetime.fromtimestamp(covidDate).date()
                if ourDate == covidDate:
                    infectedNum = int(stData.iloc[j][2])
                    if infectedNum != 0:
                        firstCase = True
                        I[j] += infectedNum
                        break
                elif covidDate > ourDate:
                    timeIndex = x
                    break

        path = "data/data" + datePath + '.xlsx'
        data = pd.read_excel(path)
        #percentAtHome = data[data['stname'] == stName]['percentAtHome'][0]
        percentAtHome = data.loc[j]['percentAtHome']
        atHome = .1 * percentAtHome / 100 * S[j]

        S.append(sGrowth(j, S[j] - atHome))
        E.append(eGrowth(j, S[j] - atHome))
        I.append(iGrowth(j))
        R.append(rGrowth(j))

        label = "infected_day" + str(j)
        mainDF.at[i, label] = I[j]

finalPath = "final/finalData.xlsx"
mainDF.to_excel(finalPath, sheet_name='main', index=False)
