import os
root =os.getcwd()
path =  root +'/Data/'
keyPath = root + "/dataKeys/"
mapPath = root+'/Maps/'


def pct_chloropleth(gpd_df, rankVar = "FTE",
                title="FTE Employment by Percentile 2018"):
    """ Draws a choropleth map color codeing the percentile of the rankvar
    requires a geopandas dataframe, and a ranking variable included in the columns
    """
    import os
    import pandas as pd
    import numpy as np
    import geopandas as gpd
    from functions import pct_map

    gpd_df['percentile'] = pct_map(gpd_df, groupVar = 'taxyear', rankVar = rankVar)

    # print(gpd_df)
    gpd_df.set_index('hex7',inplace=True)

    x = gpd_df.geometry.centroid.x.median()
    y = gpd_df.geometry.centroid.y.median() - 0.0

    import plotly.express as px
    fig = px.choropleth_mapbox(gpd_df,
                    geojson=gpd_df.geometry,
                    locations=gpd_df.index,
                    color="percentile",
                        mapbox_style = "open-street-map",
                        animation_frame='taxyear',
                        color_continuous_scale="RdYlGn",
                        center = {"lat":y, "lon":x},
                        title=title,
                    opacity=0.5,
    width=1000,height=600,zoom=8.4)
    fig.update_layout(margin={"r":0,"t":30,"l":0,"b":30}, title_x=0.5
    )
    # fig.update_geos(fitbounds="locations")
    return fig


import os
import pandas as pd
import numpy as np
# import geopandas as gpd
import plotly.express as px

# os.chdir("/data/workspace_files/")

def ageband_histogram(dff=None,metro=None, taxyear = None):


    title = "FTE Employment by Age"
    if metro != None:
        title = metro + " " + title
    if taxyear != None:
        title += " "+str(taxyear)

    if dff == None:
        dff = pd.read_csv("data/Metro_FTE_AgeBand.csv")
        dff.FTE = dff.FTE.replace("<10", "0").astype("float")

    # filter according to metro and taxyear requirements
    if metro == None: # where metro is set to all
        if taxyear == None: # all taxyears
            dff = dff.groupby(['taxyear','age_group'])['FTE'].sum().reset_index()
        else:
            dff = dff[dff.taxyear == taxyear]

    else: # where metro is selected
        dff = dff[dff.metro == metro]
        if taxyear == None:
            dff = dff.groupby(['taxyear','age_group'])['FTE'].sum().reset_index()


    dff['color'] = True
    # print(df)
    from functions import band_sort
    band_order = band_sort(dff, band="age_group")

    import plotly.express as px
    if taxyear ==None:
        fig = px.bar(dff, x="age_group", y="FTE",
                     animation_frame="taxyear",
                     animation_group="age_group",
                     color_discrete_map={True: '#c4d82d'},
                     color='color',
                     category_orders={"age_group": band_order},
                     height=600,
                     width=1000,
                     title=title,
                     labels={
                         "FTE": "FTE Employment",
                         "age_group": "Age Group",
                         "taxyear": "Tax Year"

                     }
                     )
    else:
        fig = px.bar(dff, x="age_group", y="FTE",
                     color_discrete_map={True: '#c4d82d'},
                     color='color',
                     category_orders={"age_group": band_order},
                     height=600,
                     width=1000,
                     title=title,
                     labels={
                         "FTE": "FTE Employment",
                         "age_group": "Age Group",
                         "taxyear": "Tax Year"

                     }
                     )

    fig.update_layout(title_x=0.5)
    fig.update_yaxes(range=[0, dff.FTE.max() * 1.05])
    fig.layout.update(showlegend=False)
    return fig
    # fig.show()

def wageband_histogram(dff=None,metro=None, taxyear = None):

    title = "FTE Employment by Wageband"
    if metro != None:
        title = metro + " " + title
    if taxyear != None:
        title += " "+str(taxyear)

    if dff == None:
        dff = pd.read_csv("data/Metro_FTE_WageBand.csv")
        dff.FTE = dff.FTE.replace("<10", "0").astype("float")

    # filter according to metro and taxyear requirements
    if metro == None: # where metro is set to all
        if taxyear == None: # all taxyears
            dff = dff.groupby(['taxyear','real_wage_band'])['FTE'].sum().reset_index()
        else:
            dff = dff[dff.taxyear == taxyear]

    else: # where metro is selected
        dff = dff[dff.metro == metro]
        if taxyear == None:
            dff = dff.groupby(['taxyear','real_wage_band'])['FTE'].sum().reset_index()


    dff['color'] = True
    # print(df)
    from functions import band_sort
    band_order = band_sort(dff, band="real_wage_band")

    import plotly.express as px
    dff['color'] = '#00afd5'
    if taxyear ==None:
        fig = px.bar(dff, x="real_wage_band", y="FTE",

                     color_discrete_map={'#00afd5': '#00afd5'},
                     animation_frame="taxyear",
                     animation_group="real_wage_band",
                     category_orders={"real_wage_band": band_order},
                     color='color',

                     height=600,
                     width=1000,
                     title=title,
                     labels={
                         "FTE": "FTE Employment",
                         "real_wage_band": "Real Wage Band",
                         "taxyear": "Tax Year"

                     }
                     )
    else:
        fig = px.bar(dff, x="real_wage_band", y="FTE",
                     color_discrete_map={'#00afd5': '#00afd5'},
                     color='color',
                     category_orders={"real_wage_band": band_order},
                     height=600,
                     width=1000,
                     title=title,
                     labels={
                         "FTE": "FTE Employment",
                          "real_wage_band": "Real Wage Band",
                         "taxyear": "Tax Year"

                     }
                     )

    fig.update_layout(title_x=0.5)
    fig.update_yaxes(range=[0, dff.FTE.max() * 1.05])
    fig.layout.update(showlegend=False)
    return fig
    # fig.show()

def firmsize_histogram(dff=None,metro=None, taxyear = None):

    title = "Firm Size by FTE Employees"
    if metro != None:
        title = metro + " " + title
    if taxyear != None:
        title += " "+str(taxyear)

    if dff == None:
        dff = pd.read_csv("data/Metro_Firms_Turnover_FirmSizeFTE.csv")
        dff.Firms = dff.Firms.replace("<10", "0").astype("float")

    # filter according to metro and taxyear requirements
    if metro == None: # where metro is set to all
        if taxyear == None: # all taxyears
            dff = dff.groupby(['taxyear',"FirmSize_FTE"])['Firms'].sum().reset_index()
        else:
            dff = dff[dff.taxyear == taxyear]

    else: # where metro is selected
        dff = dff[dff.metro == metro]
        if taxyear == None:
            dff = dff.groupby(['taxyear',"FirmSize_FTE"])['Firms'].sum().reset_index()


    dff['color'] = True
    # print(df)
    from functions import band_sort
    band_order = band_sort(dff, band="FirmSize_FTE")

    import plotly.express as px
    dff['color'] = True
    if taxyear ==None:
        fig = px.bar(dff, x="FirmSize_FTE", y="Firms",
                     animation_frame="taxyear",
                     animation_group="FirmSize_FTE",
                     color='color',
                     color_discrete_map={True: "#fdb813"},

                     category_orders={"FirmSize_FTE": band_order},
                     # color='#c4d82d',
                     height=600,
                     width=1000,
                     title=title,
                     labels={
                         "FirmSize_FTE": "FTE Employees",
                         "Firms": "Number of Firms"

                     }
                     )

    else:
        fig = px.bar(dff, x="FirmSize_FTE", y="Firms",
                     color='color',
                     color_discrete_map={True: "#fdb813"},

                     category_orders={"FirmSize_FTE": band_order},
                     # color='#c4d82d',
                     height=600,
                     width=1000,
                     title=title,
                     labels={
                         "FirmSize_FTE": "FTE Employees",
                         "Firms": "Number of Firms"

                     }
                     )

    fig.update_layout(title_x=0.5)
    fig.update_yaxes(range=[0, dff.Firms.max() * 1.05])
    fig.layout.update(showlegend=False)
    return fig
    # fig.show()



if __name__ == '__main__':


    import pandas as pd
    import numpy as np
    import geopandas as gpd
    os.chdir(path)
    hex_df = pd.read_csv("hex7_Panel_1_CPT.csv")
    hex_df.FTE = hex_df.FTE.replace("<10", np.nan).astype("float")
    
    os.chdir(mapPath)
    gpd_df = gpd.read_file('UberH3_7.shp')
    # print(gpd_df)

    gpd_df = gpd_df.merge(hex_df, on="hex7")

    # Limit to 2018
    gpd_df = gpd_df[gpd_df.taxyear == 2018]
    fig = pct_chloropleth(gpd_df, rankVar = "FTE")
    fig.show()