import pandas as pd

groupDict = {'Metro':'metro',"hex7":"hex7","PC":"Bus_PostalCode"}

def pct_map(df, groupVar = "taxyear", rankVar = "FTE"):
    """
    function produces a percentile measure of a given 
    rankVar: numerical ranking variable
    groupVar: subgroup for ranking, given that you map for 
    a single metro-spatial combination at a time
    """
    out = df.dropna().copy()
    out.loc[:,rankVar] = out[rankVar].astype("float")

    out.loc[:,'taxyear'] = out['taxyear'].astype('int')
    out.loc[:,'percentile'] = out.groupby(groupVar)[rankVar].rank(pct=True)
    return out['percentile']


def band_sort(df, band= "real_wage_band"):
    # Gives the sorting of the band for use in the graph
    dff = df.copy()
    x = dff[band].str.split('[',expand=True)
    x = x.iloc[:,1].str.split(',',expand=True)
    # print(x)
    x = x.iloc[:,0].astype('float')
    dff['band'] = x
    x = dff.sort_values('band')
    x = x[band].drop_duplicates(keep="first")
    # print(x)
    return x

def cum_dist(df, band = "real_wage_band"):
    # Gives the cumulative densitiy function by wageband
    dff = df.copy()
    x = dff[band].str.split(', ',expand=True)
    x = x.iloc[:,1].str.split(')',expand=True)
    x = x.iloc[:,0].astype('float')

    dff['b'] = x
    dff = dff.sort_values(['metro','taxyear','b'])

    total = dff.groupby(['metro','taxyear'])['FTE'].sum()
    total.name = "total_FTE"

    dff['cum_total'] = dff.groupby(['metro','taxyear'])['FTE'].cumsum()
    dff.set_index(['metro','taxyear'],inplace=True)
    dff = pd.merge(dff,total, right_index=True, left_index=True)
    dff['cum_perc'] = dff.cum_total / dff.total_FTE

    return dff[[band,'cum_perc']]

def gen_cum_growth(df, x="FTE", group='PC', time='taxyear'):
    # Takes the data and generates absolute growth of the x variable
    # over the time variable at a given group level

    # reshape the data to sort 1 row per year
    if group != 'c5':
        group_id = groupDict[group]
    else: group_id = group
    
    dff = df.reset_index(drop=False)
    dff.FTE = dff.FTE.replace("<10", 0).astype('float')
    dff = dff.pivot(index=time, columns=group_id, values=x)

    growth = dff.diff()
    growth.fillna(0, inplace=True)
    cum_growth = growth.cumsum()
    out = pd.concat((growth.stack(), cum_growth.stack()), axis=1)
    # out = out.reset_index(drop=False)
    out.columns = [x + "_growth", x + "_cum_growth"]
    return out

def industry_growth(metro="Cape Town"):
    fileName = "Metro_FTE_IndustrySIC5_5d.csv"
    df =pd.read_csv("Data/"+fileName)
    df = df[df.metro == metro]
    df.FTE = df.FTE.replace("<10",0).astype('float')
    df = df.dropna()
    df =df.drop_duplicates(['metro','SIC5_5d','taxyear'],keep="first")
    # print(df)
    dff = df.pivot(index='taxyear',columns=['SIC5_5d','metro'],values='FTE')

    delta = dff.diff()
    # print(delta)
    c_sum  = delta.cumsum()
    out = pd.concat((delta.stack(level=0),c_sum.stack(level=0)), axis =1)
    out.columns = ['change', 'cumulative_change']
    out.reset_index(drop=False, inplace=True)
    # print(df)
    out['c1'] = [label_sic(x)[1] for x in out.SIC5_5d]
    out['c5'] = [label_sic(x)[-1] for x in out.SIC5_5d]

    df = df[df.taxyear == 2013]
    out.set_index('SIC5_5d',inplace=True)
    df.set_index('SIC5_5d', inplace=True)
    out = pd.merge(out,df['FTE'], right_index=True, left_index=True)

    out.to_csv("sector_employment_growth.csv")
    return out.sort_values('cumulative_change')

keyPath = '/Users/kris/Desktop/NT_AdministrativeTaxDataOutputs/dataKeys/'
sicKey = pd.read_csv(keyPath + "sic5Key.csv", index_col ="key" )

def label_sic(x):

    try:
        c1 = sicKey['c1'].loc[x]
        c5 = sicKey['name'].loc[x]
        # if len(c1)>1:
            # print(c1)
        return x,str(c1),str(c5)
    except KeyError:
        print("SIC5 CODE ERROR:", x)
        return x,"Unknown","Unknown"
# def dominant_industry(group="hex7"):

def full_sic_keys():
    sic_codes = pd.read_excel('dataKeys/sic5codes.xlsx')
    full =[]
    cols=[]
    sic_codes.sic5_1d.str.split('.', expand=True)[0]
    for i in range(1,6):
        cols.append("SIC5_"+str(i)+"d")
        full.append(sic_codes["sic5_"+str(i)+"d"].str.split('.', expand=True)[0].astype('int'))
    out = pd.concat(full, axis=1)
    out.columns = cols
    return out

def band_midpoint(df,band="FirmSize_FTE"):

    dff = df[band].str.split(', ', expand=True)
    dff.iloc[:,0] = dff.iloc[:,0].str.replace("[","").astype('float')
    dff.iloc[:, 1] = dff.iloc[:, 1].str.replace(")", "").astype('float')
    return dff.mean(axis=1)

if __name__=="__main__":
    pass

