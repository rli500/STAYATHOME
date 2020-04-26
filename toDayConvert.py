import pandas as pd
# start dates for data
month = "3"
date = "8"
intmonth = int(month)
intdate = int(date)

# loop that loops through all of March and up to current April data
while(((intmonth == 3) & (intdate <= 31)) | ((intmonth == 4) & (intdate <= 21))):
    # append a 0 if single digit number for file formatting
    if (intdate < 10):
        date = "0" + date
        intdate = int(date)

    # read csv
    data = pd.read_csv("2020/0" + month + "/" + date + "/2020-0" + month + "-" + date + "-social-distancing.csv")
    main = pd.read_csv("us-state-ansi-fips.csv")

    main['totalCount'] = 0
    main['atHome'] = 0
    main['percentAtHome'] = 0

    # load data into dataframe
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

        # rough percentage calculator
        if (i % 20000 == 0):
            print(i / num * 100)

    # put dataframe into easy to use excel sheet
    path = r"dataframes\data" + month + "-" + date + ".xlsx"
    main.to_excel(path, sheet_name='main', index = False)

    # increment day
    intdate += 1
    date = str(intdate)

    # swap months if the last day of March is reached
    if (intdate == 31):
        intmonth += 1
        month = str(intmonth)
        intdate = 1
        date = str(intdate)