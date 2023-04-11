import pandas as pd
import numpy as np
import streamlit as st
import os
from collections import OrderedDict


def filterClean(path, var ='FTE', municipality='CPT', time='TaxYear', groupbyList=None):
    df = pd.read_csv(path)
    df[var] = df[var].str.replace('<10','0').astype('float')

    if municipality == 'South Africa':
        print('ALL SA')
    else:
        df = df[df.CAT_B == municipality]

    if groupbyList == None:
        groupby = [time]

    else: 
        groupby = [time] + groupbyList

    df = df.groupby(groupby)[var].sum().reset_index()
    return df


def filterCleanDf(df, var ='FTE', municipality='CPT', time='TaxYear', groupbyList=None):
    

    if municipality == 'South Africa':
        print('ALL SA')
    else:
        df = df[df.CAT_B == municipality]

    if groupbyList == None:
        groupby = [time]

    else: 
        groupby = [time] + groupbyList

    df = df.groupby(groupby)[var].sum().reset_index()
    return df




@st.cache
def get_keys():
    key1 = pd.read_csv('keys/key1d.csv')
    key1.columns = ['SIC7_1d','Sector']
    key2 = pd.read_csv('keys/sic7_2d_codes.csv')
    # st.write(key2)
    key2.columns = ['SIC7_1d','SIC7_2d','Sector','Industry']
    key5 = pd.read_csv('keys/sic7_5d_codes.csv')
    key5.columns = ['SIC7_5d','Industry']
    return key1,key2, key5

key1, key2, key5 = get_keys()


@st.cache(allow_output_mutation=True)
def industry_employment(municipality):
    industryEmployment = filterCleanDf(industryFTEdf, var = 'FTE', time='month', municipality=municipality, groupbyList=['SIC7_1d','SIC7_5d'])
    industryEmployment = pd.merge(industryEmployment,key1, right_on="SIC7_1d",left_on="SIC7_1d")
    industryEmployment = pd.merge(industryEmployment,key5, right_on="SIC7_5d",left_on="SIC7_5d")
    return industryEmployment

@st.cache(allow_output_mutation=True)
def get_industry_fte():
    df= pd.read_parquet("Data/Municipal_FTE_Industry5d_Monthly.parquet")
    df['FTE'] = df["FTE"].str.replace('<10','0').astype('float')
    return df

industryFTEdf = get_industry_fte()
# @st.cache(allow_output_mutation=True)
# def getAllEstablishments():
#     df = pd.read_csv("Data/Municipal_Establishments_Industry2d.csv")
#     df['Establishments'] = df['Establishments'].str.replace('<10','0').astype('float')
#     df = pd.merge(df,key2, right_on="SIC7_2d",left_on="SIC7_2d")
    
#     return df
# allEstablishmentDf = getAllEstablishments()

# pd.DataFrame
# pd.DataFrame(industryEstablishments.CAT_B.unique())

industry = pd.DataFrame(industryFTEdf.CAT_B.unique())
industry.columns = ['Municipality']
industry['len'] = industry.Municipality.str.len()
industry = industry.sort_values(by='len', ascending=True)
# st.write()

st.write("## Employment impact of COVID-19 Dashboard")

with st.sidebar:
    municipality = st.selectbox('Select a municipality',["South Africa"] + list(industry.Municipality),index=8)
    # st.write('View')
    # view  = st.radio('View', ['TaxYear','Month'], index=1, horizontal=True)
    view = 'Month'
    st.write('Figure Settings')
    height = st.slider('height', 300, 900, 600,step=50)
    width = st.slider('width', 500, 1600, 900,step=50)
    industryEmployment = industry_employment(municipality)



# @st.cache
# def getIndustryEstablishments(municipality):
#     # industryEstablishments = filterCleanDf(allEstablishmentDf, var = 'Establishments', municipality=municipality, groupbyList=["SIC7_1d","SIC7_2d"])
#     industryEstablishments = pd.merge(allEstablishmentDf,key2, right_on="SIC7_2d",left_on="SIC7_2d")
#     return industryEstablishments
# industryEstablishments = getIndustryEstablishments(municipality)

employment, wages, demographics = st.tabs(['Employment', 'Wages', 'Demographics'])

# with firms:
#     # industryEstablishments = getIndustryEstablishments(municipality).drop_duplicates()
#     # st.write(allEstablishmentDf)
#     # st.write(industryEstablishments)


#     def checkAllEstablishmentGrowth(industryEstablishments):
#         sectors = filterCleanDf(industryEstablishments,time='month',municipality=municipality,groupbyList=['Sector','Industry'])
#         change = []
#         df = sectors.groupby(['Sector','Industry','TaxYear'])["Establishments"].sum().reset_index()
#         for sector in sectors['Industry'].unique():
#             diffDf = pd.DataFrame(df[df['Industry']==sector].sort_values('TaxYear')['Establishments'].diff(1))
#             diffDf.columns = ['Establishment Change']
#             diffDf['pct_change'] = pd.DataFrame(df[df['Industry']==sector].sort_values('month')['Establishments'].pct_change(1))
#             diffDf["month"]  = sorted(sectors.month.unique())
#             diffDf['Industry'] = sector
#             change.append(diffDf)

#         change = pd.concat(change,axis=0)
#         # df.set_index(['month','SIC7_1d'],inplace=True)
#         # change = pd.merge(df,change,left_index=True,right_index=True).reset_index()
#         # change = pd.merge(change,key1, right_on="SIC7_1d",left_on="SIC7_1d")
#         return change
#     st.write(checkAllEstablishmentGrowth(industryEstablishments))

with employment:
    import plotly.express as px
    
    if view == 'Month':

        def checkAllFTEGrowth(years=12,group='SIC7_1d',var='FTE'):
            sectors = filterCleanDf(industryFTEdf,time='month',municipality=municipality,groupbyList=['SIC7_1d'])
            change = []
            df = sectors.groupby([group,'month'])[var].sum().reset_index()
            for sector in sectors[group].unique():
                diffDf = pd.DataFrame(df[df[group]==sector].sort_values('month')['FTE'].diff(years))
                diffDf.columns = [var+'_delta']
                diffDf['pct_change'] = pd.DataFrame(df[df[group]==sector].sort_values('month')['FTE'].pct_change(12))
                diffDf["month"]  = sorted(sectors.month.unique())
                diffDf[group] = sector
                change.append(diffDf)

            change = pd.concat(change,axis=0).set_index(['month','SIC7_1d'])
            df.set_index(['month','SIC7_1d'],inplace=True)
            change = pd.merge(df,change,left_index=True,right_index=True).reset_index()
            change = pd.merge(change,key1, right_on="SIC7_1d",left_on="SIC7_1d")
            return change.sort_values('month'), sectors
        
        
        change, sectors = checkAllFTEGrowth(years=1,group='SIC7_1d',var='FTE')



        figDf = change.pivot(index='month',columns='Sector',values='FTE').sort_index().diff(12).iloc[-36:,:].stack().reset_index()
        figDf.columns = ['Month','Sector','FTE change y-o-y']
        fig = px.bar(figDf,x='Month',y='FTE change y-o-y',
        color='Sector',
        title='Year-on-Year Changes in FTE Employment',
        height = height,
        width = width,
        color_discrete_sequence=px.colors.qualitative.Alphabet)
        fig.update_layout(title_x=0.5)
        y0 = figDf[figDf['FTE change y-o-y'] < 0]
        y0 = y0.groupby(figDf['Month'])['FTE change y-o-y'].sum().min() - 200
        # st.write(y0)
        fig.add_shape(
            type='rect',
            x0=figDf['Month'].min(), x1=figDf['Month'].max(),
            y0=y0, 
            y1=0,
            fillcolor='tomato',
            opacity=0.2,
            line=dict(color='tomato'),
            layer='below'  # Set the layer to 'below' to place the shape behind the traces
        )

        # Extract the discrete color mapping
    color_mapping = {}
    for trace in fig.data:
        category = trace.offsetgroup  # Get the category from the custom data
        color = trace.marker.color  # Get the color associated with the category
        color_mapping[category] = color
    st.plotly_chart(fig)



    


    months = sorted(sectors.month.unique())
    month  = st.select_slider('month',options=months,value=months[-1])
    
    fig = px.sunburst(industryEmployment[industryEmployment.month == month], path=['Sector','Industry'], 
                 values='FTE', 
                 color='Sector',
                title="FTE Sectoral Composition "+month+": 1D & 5D",
                    color_discrete_map= color_mapping,
                    width =width,height=height)
    fig.update_layout( title_x=0.5)
    fig.update_yaxes(automargin=True)
    fig.update_traces(textinfo='percent root + label')
    st.plotly_chart(fig)


    with st.expander('View Bar Chart Data'):
        st.write(figDf)

    with st.expander('View Pie Chart Data'):
        st.write(industryEmployment)


    
    # st.write(industryEmployment )
with demographics:
    import pandas as pd
    import numpy as np
    if view == 'Month':
        
        @st.cache
        def youthEmployment():
            df =  pd.read_parquet('Data/Municipal_FTE_Youth_Sex_Monthly.parquet')
            # st.write(df)
            # df.Youth  = df.Youth.str.replace("[35, 120)",">=35")
            # df.Youth  = df.Youth.str.replace("[35.0, 120.0)",">=35")
            df.FTE = df.FTE.str.replace("<10","0").astype('float')
            df.Youth  = df.Youth.str.replace("\\.0","")
            
            keep = [x  in ['[15, 25)', '[15.0, 25.0)', '[25, 35)', '[25.0, 35.0)'] for x in df.Youth]
            df['ageGroup' ] = df.Youth.copy()
            df['Youth'] = keep
            df['Age'] = 'Over 35 Y.O.'
            df.Age[df.Youth] =  "Under 35 Y.O."
            df['Group']=df['Sex'] +" "+df['Age']
            return df
        yDf = youthEmployment()

        def load_youth_data(municipality='CPT'):
            youthDf = filterCleanDf(yDf, var ='FTE', municipality=municipality, time='month', groupbyList=['Youth','Sex'])

            # youthDf.Youth.unique()

           
            
            youthDf = youthDf.groupby(['month','Youth','Sex'])['FTE'].sum().reset_index()
            youthDf['FTE change y-o-y'] = None
            youthDf['FTE % change y-o-y'] = None
            youthDf['Age'] = 'Over 35 Y.O.'
            youthDf.Age[youthDf.Youth] =  "Under 35 Y.O."

            return youthDf
        
        youthDf = load_youth_data(municipality=municipality)
        for gender in ['F','M','Unknown']:
            for youth in [True,False]:
                selection = np.logical_and(youthDf.Sex == gender, youthDf.Youth == youth)
                youthDf['FTE change y-o-y'][selection] = youthDf[selection].sort_values('month')['FTE'].diff(12)
                youthDf['FTE % change y-o-y'][selection] = youthDf[selection].sort_values('month')['FTE'].pct_change(12)

        import plotly.express as px



        youthDf['Group'] =youthDf['Sex'] +" "+youthDf['Age']
        colorMap = {'F Over 35 Y.O.':"#CA3433",
        'F Under 35 Y.O.':"#FA8072",
        'M Over 35 Y.O.':"#0F4D92",
        'M Under 35 Y.O.':"#89CFF0",
        'Unknown Over 35 Y.O.':"Black",
        'Unknown Under 35 Y.O.': "#808080"}

        figDf = youthDf.dropna().iloc[-12*3*3*2:]
        fig = px.bar(figDf,x='month',y='FTE change y-o-y',
        color='Group',
        color_discrete_map=colorMap,
        title='Year-on-Year Changes in FTE Employment by Gender and Age',
        height = height,
        width=width,
        color_discrete_sequence=px.colors.qualitative.Alphabet)
        fig.update_layout(title_x=0.5)
        y0 = figDf[figDf['FTE change y-o-y'] < 0]
        y0 = y0.groupby(figDf['month'])['FTE change y-o-y'].sum().min() - 200
        fig.add_shape(
            type='rect',
            x0=figDf['month'].min(), x1=figDf['month'].max(),
            y0=y0, y1=0,
            fillcolor='tomato',
            opacity=0.2,
            line=dict(color='tomato'),
            layer='below'  # Set the layer to 'below' to place the shape behind the traces
        )
        st.plotly_chart(fig)

        month  = st.select_slider('month',options=months,value=months[-1], key='month3')
        fig = px.sunburst(yDf[yDf.month == month], path=['Group','ageGroup'], 
                 values='FTE', 
                 color='Group',
                title="Employment Demographics "+month,
                    color_discrete_map= colorMap ,
                    width =width,height=height)
        fig.update_layout( title_x=0.5)
        fig.update_yaxes(automargin=True)
        fig.update_traces(textinfo='percent root + label')
        st.plotly_chart(fig)

        st.write(yDf)

with wages:
    @st.cache
    def getWages():

        wages = pd.read_parquet('Data/Municipal_FTE_WageBand_Monthly.parquet')
        wages.FTE = wages.FTE.str.replace("<10","0").astype('float')
        return wages
    if view == 'Month':
        monthlyWageDf = filterCleanDf(wages, var ='FTE', municipality=municipality, time='month', groupbyList=['RealWageBand'])
        figDf = monthlyWageDf.pivot(index='month', columns='RealWageBand', values='FTE').sort_index().diff().stack().reset_index().rename(columns={0: 'FTE change y-o-y'}).dropna().sort_values(['month','RealWageBand'])[-14*3*12:]

        color_shades = OrderedDict({
            '[0.0, 400.0)': "#FFA07A",       # Light Salmon
            '[400.0, 800.0)': "#FA8072",     # Salmon
            '[800.0, 1600.0)': "#E9967A",    # Dark Salmon
            '[1600.0, 3200.0)': "#F08080",   # Light Coral
            '[3200.0, 6400.0)': "#CD5C5C",   # Indian Red
            '[6400.0, 12800.0)': "#9ACD32",  # Yellow Green
            '[12800.0, 25600.0)': "#7CFC00", # Lawn Green
            '[25600.0, 51200.0)': "#32CD32", # Lime Green
            '[51200.0, 102400.0)': "#228B22",# Forest Green
            '[102400.0, 204800.0)': "#008000",# Green
            '[204800.0, 409600.0)': "#0000CD",# Medium Blue
            '[409600.0, 819200.0)': "#000080",# Navy Blue
            '[819200.0, 1638400.0)': "#191970",# Midnight Blue
            '[1638400.0, 10000000.0)': "#000000" # Black
        })


        fig = px.bar(figDf,
                    x="month",
                    y='FTE change y-o-y',
                    color="RealWageBand",
                    color_discrete_map=color_shades,
                    category_orders={"RealWageBand": list(color_shades.keys())},  # Specify the order of categories in the legend
                    width=width,
                    height=height
                    )
        
        y0 = figDf[figDf['FTE change y-o-y'] < 0]
        y0 = y0.groupby(figDf['month'])['FTE change y-o-y'].sum().min() - 200
        # st.write(y0)
        fig.add_shape(
            type='rect',
            x0=figDf['month'].min(), x1=figDf['month'].max(),
            y0=y0, 
            y1=0,
            fillcolor='tomato',
            opacity=0.2,
            line=dict(color='tomato'),
            layer='below'  # Set the layer to 'below' to place the shape behind the traces
        )


        st.plotly_chart(fig)
        month  = st.select_slider('month',options=months,value=months[-1], key='month2')
        fig = px.sunburst(monthlyWageDf[monthlyWageDf.month == month], path=['RealWageBand'], 
                 values='FTE', 
                 color='RealWageBand',
                title="Wages Composition "+month,
                    color_discrete_map= color_shades ,
                    width =width,height=height)
        fig.update_layout( title_x=0.5)
        fig.update_yaxes(automargin=True)
        fig.update_traces(textinfo='percent root + label')
        st.plotly_chart(fig)