import pandas as pd
data = pd.read_csv("socialdistancing/2020/01/01/2020-01-01-social-distancing.csv")
main = pd.read_csv("fips/us-state-ansi-fips.csv")

main['before_total'] = 0
main['before_athome'] = 0
main['before_percent'] = 0

num = data.shape[0]
for i in range(num):
    fipsID = data['origin_census_block_group'][i]
    fipsID = int(fipsID//1e10)

    index = main.index[main['st'] == fipsID]

    deviceCount = data['device_count'].iloc[i] + main.loc[index, 'before_total']
    atHome = data['completely_home_device_count'].iloc[i] + main.loc[index, 'before_athome']

    main.loc[index, 'before_total'] = deviceCount
    main.loc[index, 'before_athome'] = atHome
    main.loc[index, 'before_percent'] = (atHome/deviceCount)*100
