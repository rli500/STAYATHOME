import pandas as pd

data = pd.read_csv("socialdistancing/2020/01/01/2020-01-01-social-distancing.csv")
main = pd.read_csv("fips/us-state-ansi-fips.csv")

main['totalCount'] = 0
main['atHome'] = 0
main['percentAtHome'] = 0

num = data.shape[0]
for i in range(num):
    fipsID = data['origin_census_block_group'][i]
    fipsID = int(fipsID//1e10)

    index = main.index[main['st'] == fipsID]

    deviceCount = data['device_count'].iloc[i] + main.loc[index, 'totalCount']
    atHome = data['completely_home_device_count'].iloc[i] + main.loc[index, 'atHome']

    main.loc[index, 'totalCount'] = deviceCount
    main.loc[index, 'atHome'] = atHome
    main.loc[index, 'percentAtHome'] = (atHome/deviceCount)*100
