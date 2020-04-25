import pandas as pd
month = "3"
date = "8"
intmonth = int(month)
intdate = int(date)
while(((intmonth == 3) & (intdate <= 31)) | ((intmonth == 4) & (intdate <= 21))):
    if (intdate < 10):
        date = "0" + date
        intdate = int(date)

    data = pd.read_csv("2020/0" + month + "/" + date + "/2020-0" + month + "-" + date + "-social-distancing.csv")
    main = pd.read_csv("us-state-ansi-fips.csv")

    main['totalCount'] = 0
    main['atHome'] = 0
    main['percentAtHome'] = 0

    num = data.shape[0]
    print(num)
    for i in range(num):
        fipsID = data['origin_census_block_group'][i]
        fipsID = int(fipsID//1e10)

        index = main.index[main['st'] == fipsID]

        deviceCount = data['device_count'].iloc[i] + main.loc[index, 'totalCount']
        atHome = data['completely_home_device_count'].iloc[i] + main.loc[index, 'atHome']

        main.loc[index, 'totalCount'] = deviceCount
        main.loc[index, 'atHome'] = atHome
        main.loc[index, 'percentAtHome'] = (atHome/deviceCount)*100

        if (i % 20000 == 0):
            print(i / num * 100)

    path = r"dataframes\data" + month + "-" + date + ".xlsx"
    main.to_excel(path, sheet_name='main', index = False)

    intdate += 1
    date = str(intdate)

    if (intdate == 31):
        intmonth += 1
        month = str(intmonth)
        intdate = 1
        date = str(intdate)