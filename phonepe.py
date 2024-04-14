import streamlit as st
from streamlit_option_menu import option_menu
import json
import pandas as pd
import mysql.connector
import plotly.express as px
import requests

#SQL connection

myDb = mysql.connector.connect(
    host = 'localhost',
    user = 'root',
    password = 'Aa12345678!',
    database = 'phonepe_visualization'
)
myCursor = myDb.cursor()

# Select Queries

myCursor.execute('Select * from aggregrated_insurance')
table_data = myCursor.fetchall()
aggr_insurance = pd.DataFrame(data= table_data, columns = ['state', 'year', 'quarter', 'transaction_type', 'transaction_count','transaction_amount'])

myCursor.execute('Select * from aggregrated_transaction')
table_data = myCursor.fetchall()
aggr_transaction = pd.DataFrame(data= table_data, columns = ['state', 'year', 'quarter', 'transaction_type', 'transaction_count','transaction_amount'])
aggr_transaction['year'] = aggr_transaction['year'].apply(pd.to_numeric)

myCursor.execute('Select * from aggregrated_user')
table_data = myCursor.fetchall()
aggr_user = pd.DataFrame(data= table_data, columns = ['state', 'year', 'quarter', 'brand', 'transaction_count', 'percentage'])

myCursor.execute('Select * from map_insurance')
table_data = myCursor.fetchall()
map_insurance = pd.DataFrame(data= table_data, columns = ['state', 'year', 'quarter', 'district', 'transaction_count', 'transaction_amount'])

myCursor.execute('Select * from map_transaction')
table_data = myCursor.fetchall()
map_transaction = pd.DataFrame(data= table_data, columns = ['state', 'year', 'quarter', 'district', 'transaction_count', 'transaction_amount'])

myCursor.execute('Select * from map_user')
table_data = myCursor.fetchall()
map_user = pd.DataFrame(data= table_data, columns = ['state', 'year', 'quarter', 'district', 'registered_users', 'app_opens'])

myCursor.execute('Select * from top_insurance')
table_data = myCursor.fetchall()
top_insurance = pd.DataFrame(data= table_data, columns = ['state', 'year', 'quarter', 'pincode', 'transaction_count','transaction_amount'])

myCursor.execute('Select * from top_transaction')
table_data = myCursor.fetchall()
top_transaction = pd.DataFrame(data= table_data, columns = ['state', 'year', 'quarter', 'pincode', 'transaction_count','transaction_amount'])

myCursor.execute('Select * from top_user')
table_data = myCursor.fetchall()
top_user = pd.DataFrame(data= table_data, columns = ['state', 'year', 'quarter', 'pincode', 'registered_users'])

#Filtering DF based on Year
def df_filter_on_year(df,year):
    #df_y: data frame filtered based on year
    df_y = df.loc[df['year'] == year]
    df_y.reset_index(drop = True, inplace = True)
    return df_y
def df_filter_on_year_quarter(df,year,quarter):
    #df_y_q: data frame filtered based on year and quarter
    df_y = df_filter_on_year(df,year)
    df_y_q = df_y.loc[df_y['quarter'] == quarter]
    df_y_q.reset_index(drop = True, inplace = True)
    return df_y_q
    
#Analysis of Transaction Amount and Count based on Year and grouped by State
def dfyq_state(df,year,quarter = None):
    if(quarter is None):
        df_y = df_filter_on_year(df,year)
        df_grouped = df_y.groupby('state')[['transaction_count','transaction_amount']].sum()
        df_grouped.reset_index(inplace = True)
        fig_bar_count = px.bar(df_grouped,x ='state' , y='transaction_count',title =  f'{year} TRANSACTION COUNT',
                            color_discrete_sequence=px.colors.sequential.Cividis,height = 600, width = 600)
        fig_bar_amount = px.bar(df_grouped,x ='state' , y='transaction_amount',title = f'{year} TRANSACTION AMOUNT' ,
                            color_discrete_sequence=px.colors.sequential.Agsunset,height = 600, width = 600)
        
        col1,col2 = st.columns(2)
        with col1:
            st.plotly_chart(fig_bar_count)
        with col2:
            st.plotly_chart(fig_bar_amount)
    
    else:
        df_y_q = df_filter_on_year_quarter(df,year,quarter)
        df_grouped = df_y_q.groupby('state')[['transaction_count','transaction_amount']].sum()
        df_grouped.reset_index(inplace = True)
        fig_bar_count = px.bar(df_grouped,x ='state' , y='transaction_count',title =  f'{year} QUARTER {quarter}: TRANSACTION COUNT',
                            color_discrete_sequence=px.colors.sequential.Cividis,height = 600, width = 600)
        fig_bar_amount = px.bar(df_grouped,x ='state' , y='transaction_amount',title = f'{year} QUARTER {quarter}: TRANSACTION AMOUNT' ,
                            color_discrete_sequence=px.colors.sequential.Agsunset,height = 600, width = 600)
        col1,col2 = st.columns(2)
        with col1:
            st.plotly_chart(fig_bar_count)
        with col2:
            st.plotly_chart(fig_bar_amount)

    url = 'https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson'
    response = requests.get(url)
    data = json.loads(response.content)
    fig_india_amount = px.choropleth(df_grouped, locations = 'state', 
                                    geojson = data,featureidkey = 'properties.ST_NM',  # USExd p.sn notation instead of ['p']['sn']
                                    color = 'transaction_amount', color_continuous_scale = 'twilight',
                                    range_color = (df_grouped['transaction_amount'].min(),df_grouped['transaction_amount'].max()),
                                    title = f'{year} TRANSACTION AMOUNT',hover_name = 'state',fitbounds = 'locations',
                                    height = 600, width = 600) 
    fig_india_amount.update_geos(visible = False)
    fig_india_count = px.choropleth(df_grouped, locations = 'state', 
                                    geojson = data,featureidkey = 'properties.ST_NM',  # USE p.sn notation instead of ['p']['sn']
                                    color = 'transaction_count', color_continuous_scale = 'viridis',
                                    range_color = [df_grouped['transaction_count'].min(),df_grouped['transaction_count'].max()],
                                    title = f'{year} TRANSACTION COUNT',hover_name = 'state',fitbounds = 'locations',
                                    height = 600, width = 600) 
    fig_india_count.update_geos(visible = False)
    # TO change title valuew for Count grouped datas
    if(quarter is not None):
        fig_india_count.update_layout(dict(title = f'{year} QUARTER {quarter}: TRANSACTION COUNT'))
        fig_india_amount.update_layout(dict(title = f'{year} QUARTER {quarter}: TRANSACTION AMOUNT'))
        
    col1,col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig_india_count)
    with col2:
        st.plotly_chart(fig_india_amount)

#Analysis of Transaction Amount and Count of Year based on State and Treansaction Type 
def dfyqs_ttype (df,year,state,quarter = None):
    if(quarter is None):
        df_y = df_filter_on_year(df,year)
        df_y_s = df_y.loc[df_y['state'] == state]
        df_grouped = df_y_s.groupby('transaction_type')[['transaction_count','transaction_amount']].sum()
        df_grouped.reset_index(inplace=True)
    else:
        df_y_q = df_filter_on_year_quarter(df,year,quarter)
        df_y_q_s = df_y_q.loc[df_y_q['state'] == state]
        df_grouped = df_y_q_s.groupby('transaction_type')[['transaction_count','transaction_amount']].sum()
        df_grouped.reset_index(inplace=True)
    
    fig_pie_count = px.pie(data_frame= df_grouped,names = 'transaction_type',values = 'transaction_count',hole = 0.5,
                            title = f'{year} {state.upper()} Transaction Count', height = 600, width = 600) 
    fig_pie_amount = px.pie(data_frame= df_grouped,names = 'transaction_type',values = 'transaction_amount',hole = 0.5,
                            title = f'{year} {state.upper()} Transaction Amount', height = 600, width = 600) 
    
    if(quarter is not None):
        fig_pie_count.update_layout(dict(title = f'{year} QUARTER {quarter}: {state.upper()} Transaction Count'))
        fig_pie_amount.update_layout(dict(title = f'{year} QUARTER {quarter}: {state.upper()} Transaction Amount'))
    
    col1,col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig_pie_count)
    with col2:
        st.plotly_chart(fig_pie_amount)
        
def dfyqs_brands(df,year,quarter = None,state = None):
    #For df filtered with year => Parameter given to func (df,year)
    if(state is None) and (quarter is None):
        df_y = df_filter_on_year(df,year)
        df_grouped = df_y.groupby('brand')['transaction_count'].sum()
        df_grouped = pd.DataFrame(df_grouped)
        df_grouped.reset_index(inplace= True)
        fig_bar_brand = px.bar(data_frame = df_grouped , x = 'brand',labels=(dict(brand = 'Brands', transaction_count = 'Transaction Count')), 
                        y = 'transaction_count', width= 800,color_discrete_sequence= px.colors.sequential.Sunsetdark,
                        hover_name= 'brand', title = f'{year} BRANDS TRANSACTION COUNT')
        st.plotly_chart(fig_bar_brand)
    
    #For df filtered with year and quarter => Parameter given to func (df,year,quarter)
    elif(state is None):
        df_y_q = df_filter_on_year_quarter(df,year,quarter)
        df_grouped = df_y_q.groupby('brand')['transaction_count'].sum() 
        df_grouped = pd.DataFrame(df_grouped)
        df_grouped.reset_index(inplace= True)
        fig_bar_brand = px.bar(data_frame = df_grouped , x = 'brand', y = 'transaction_count', 
                           labels=(dict(brand = 'Brands', transaction_count = 'Transaction Count')),
                           width= 800,color_discrete_sequence= px.colors.sequential.Sunsetdark,
                           hover_name= 'brand', title = f'{year} QUARTER {quarter}: BRANDS TRANSACTION COUNT') 
        st.plotly_chart(fig_bar_brand)
    
    #For df filtered with year, quarter and state => Parameter given to func (df,year,quarter,state)  
    else:
        df_y_q = df_filter_on_year_quarter(df,year,quarter)
        df_y_q_s = df_y_q.loc[df_y_q['state'] == state]
        df_grouped = df_y_q_s.groupby('brand')[['transaction_count','percentage']].sum()
        df_grouped.reset_index(inplace = True)   
        fig_line_brand  = px.line(data_frame = df_grouped, x= 'brand',y = 'transaction_count',hover_data ='percentage', hover_name= 'brand',
                                  title = f'{year} QUARTER {quarter}: {state} BRANDS TRANSACTION COUNT')  
        st.plotly_chart(fig_line_brand)

def dfyqs_district(df,year,state,quarter = None):
    if quarter is None:
        df_y = df_filter_on_year(df,year)
        dfy_s = df_y.loc[df_y['state'] == state]
        df_grouped = dfy_s.groupby('district')[['transaction_count','transaction_amount']].sum()
        df_grouped.reset_index(inplace= True)
        fig_bar_count = px.bar(data_frame= df_grouped,x = 'transaction_count', y = 'district',orientation='h',
                            title = f'{year} {state.upper()} Transaction Count', height = 600, width = 600,
                            color_discrete_sequence = px.colors.sequential.Mint_r) 
        fig_bar_amount = px.bar(data_frame= df_grouped,x = 'transaction_amount', y = 'district',orientation='h',
                            title = f'{year} {state.upper()} Transaction Amount', height = 600, width = 600,
                            color_discrete_sequence = px.colors.sequential.Agsunset_r)
    
    else: 
        df_y_q = df_filter_on_year_quarter(df,year,quarter)
        dfy_q_s = df_y_q.loc[df_y_q['state'] == state]
        df_grouped = dfy_q_s.groupby('district')[['transaction_count','transaction_amount']].sum()
        df_grouped.reset_index(inplace= True)
        fig_bar_count = px.bar(data_frame= df_grouped,x = 'transaction_count', y = 'district',orientation='h',
                            title = f'{year} QUARTER {quarter}: {state.upper()} Transaction Count', height = 600, width = 600,
                            color_discrete_sequence = px.colors.sequential.Mint_r) 
        fig_bar_amount = px.bar(data_frame= df_grouped,x = 'transaction_amount', y = 'district',orientation='h',
                            title = f'{year} QUARTER {quarter}: {state.upper()} Transaction Amount', height = 600, width = 600,
                            color_discrete_sequence = px.colors.sequential.Agsunset_r)
    
    col1,col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig_bar_count)
    with col2:    
        st.plotly_chart(fig_bar_amount)
#Map User line chart        
def dfyq_state_user(df,year,quarter = None):
    if(quarter is None):
        df_y = df_filter_on_year(df,year)
        df_grouped = df_y.groupby('state')[['registered_users','app_opens']].sum()
        df_grouped.reset_index(inplace = True)
        fig_line_user = px.line(df_grouped,x ='state' , y=['registered_users','app_opens'],title =  f'{year} REGISTERED USERS AND APP OPENS',
                            color_discrete_sequence=px.colors.sequential.Viridis,height = 800, width = 800, markers='lines+markers')  #change color or keep it side by side
    else:
        df_y_q = df_filter_on_year_quarter(df,year,quarter)
        df_grouped = df_y_q.groupby('state')[['registered_users','app_opens']].sum()
        df_grouped.reset_index(inplace = True)
        fig_line_user = px.line(df_grouped,x = 'state' , y = ['registered_users','app_opens'],title =  f'{year} QUARTER {quarter}: REGISTERED USERS AND APP OPENSS',
                                        height = 800, width = 800, markers='lines+markers')  
        
    st.plotly_chart(fig_line_user)

# Map User Bar Chart 
def dfyqs_district_user(df,year,state,quarter = None):
    if quarter is None:
        df_y = df_filter_on_year(df,year)
        dfy_s = df_y.loc[df_y['state'] == state]
        df_grouped = dfy_s.groupby('district')[['registered_users','app_opens']].sum()
        df_grouped.reset_index(inplace= True)
        fig_bar_reg_users = px.bar(data_frame= df_grouped,x = 'registered_users', y = 'district',orientation='h',
                            title = f'{year} REGISTERED USERS', height = 600, width = 600,
                            color_discrete_sequence = px.colors.sequential.Mint_r) 
        fig_bar_app_opens = px.bar(data_frame= df_grouped,x = 'app_opens', y = 'district',orientation='h',
                            title = f'{year} APP OPENS', height = 600, width = 600,
                            color_discrete_sequence = px.colors.sequential.Agsunset_r)
    
    else: 
        df_y_q = df_filter_on_year_quarter(df,year,quarter)
        dfy_q_s = df_y_q.loc[df_y_q['state'] == state]
        df_grouped = dfy_q_s.groupby('district')[['registered_users','app_opens']].sum()
        df_grouped.reset_index(inplace= True)
        fig_bar_reg_users = px.bar(data_frame= df_grouped,x = 'registered_users', y = 'district',orientation='h',
                            title = f'{year} QUARTER {quarter}: REGISTERED USERS', height = 600, width = 600,
                            color_discrete_sequence = px.colors.sequential.Mint_r) 
        fig_bar_app_opens = px.bar(data_frame= df_grouped,x = 'app_opens', y = 'district',orientation='h',
                            title = f'{year} QUARTER {quarter}: APP OPENS', height = 600, width = 600,
                            color_discrete_sequence = px.colors.sequential.Agsunset_r)
    
    col1,col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig_bar_reg_users)
    with col2:    
        st.plotly_chart(fig_bar_app_opens)

# Top Insurance Bar Plot        
def dfys_quarter (df,year,state):
    df_y = df_filter_on_year(df,year)
    df_y_s = df_y.loc[df_y['state'] == state]
    df_y_s.reset_index(drop = True,inplace=True) 
    fig_bar_count = px.bar(data_frame= df_y_s , x=  'quarter', y ='transaction_count',hover_name='pincode',
                        title = f'{year} {state.upper()} Transaction Count', height = 600, width = 600,
                        color_discrete_sequence = px.colors.sequential.Mint_r) 
    fig_bar_amount = px.bar(data_frame= df_y_s,x = 'quarter', y = 'transaction_amount',hover_name='pincode',
                        title = f'{year} {state.upper()} Transaction Amount', height = 600, width = 600,
                        color_discrete_sequence = px.colors.sequential.Agsunset_r)
    
    col1,col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig_bar_count)
    with col2:
        st.plotly_chart(fig_bar_amount)

# Top User Bar Plot
def dfy_state_quarter(df,year,quarter = None):
    if (quarter is None):
        df_y = df_filter_on_year(df,year)
        df_grouped = df_y.groupby(['state',"quarter"])[['registered_users']].sum()
        df_grouped.reset_index(inplace = True)
    else:
        df_y_q = df_filter_on_year_quarter(df,year,quarter)
        df_grouped = df_y_q.groupby(['state'])[['registered_users']].sum()
        df_grouped.reset_index(inplace = True)
    fig_bar_reguser = px.bar(data_frame=df_grouped, x = "state",y = "registered_users",
                            height = 800, width = 800,color_discrete_sequence=px.colors.sequential.Aggrnyl_r,
                            hover_name="state", title = f'{year} Registered Users',color = 'registered_users')
    if(quarter is not None):
        fig_bar_reguser.update_layout(dict(title = f'{year} QUARTER {quarter}: Transaction Count'))
    st.plotly_chart(fig_bar_reguser)
        

def dfys_quarter_pincode(df,year,state,quarter = None):
    if(quarter is None):
        df_y = df_filter_on_year(df,year)
        df_y_s = df_y.loc[df_y["state"] == state]
        df_grouped = df_y_s.groupby(["quarter",'pincode']).sum()
        df_grouped.reset_index(inplace= True)
        fig_bar_reguser = px.bar(data_frame=df_grouped, x = "quarter",y = "registered_users",
                                height = 800, width = 800,color_discrete_sequence=px.colors.sequential.Aggrnyl_r,
                                hover_name="pincode", title = f'{year} Registered Users',color = 'registered_users')
        st.plotly_chart(fig_bar_reguser)
    else:
        df_y_q = df_filter_on_year_quarter(df,year,quarter)
        df_y_q_s = df_y_q[df_y_q['state'] == state]
        df_grouped = df_y_q_s.groupby(['pincode'])[['registered_users']].sum()
        df_grouped.reset_index(inplace = True)
        fig_bar_reguser = px.pie(data_frame=df_grouped, 
                                 values="registered_users",
                                 names="pincode",
                                 hover_name = 'pincode',
                                 title = 'States Registered Users by Pincode')
        st.plotly_chart(fig_bar_reguser)

    
        

       
#Streamlit UI
#Layout

st.set_page_config(layout='wide')
st.title(' :violet[Phonepe Pulse Data Visualization and Exploration]')

with st.sidebar:
    
    selected = option_menu("Menu", ["Home", "Explore Data", "Top Charts", "About"], 
                icons = ["house","graph-up-arrow","bar-chart-line", "exclamation-circle"],
                menu_icon = "menu-button-wide",
                default_index = 0,
                styles = {"nav-link": {"font-size": "20px", "text-align": "left", "margin": "-2px", "--hover-color": "#6F36AD"},
                        "nav-link-selected": {"background-color": "#6F36AD"}})

if selected == "Home":
    st.image("/Users/allen/Documents/Py VE/Includes/img.png")
    st.markdown("# :violet[Data Visualization and Exploration]")
    st.markdown("## :violet[A User-Friendly Tool Using Streamlit and Plotly]")
    col1,col2 = st.columns([3,2],gap="medium")
    with col1:
        st.write(" ")
        st.write(" ")
        st.markdown("### :violet[Domain :] Fintech")
        st.markdown("### :violet[Technologies used :] Github Cloning, Python, Pandas, MySQL, mysql-connector-python, Streamlit, and Plotly.")
        st.markdown("### :violet[Overview :] In this streamlit web app you can visualize the phonepe pulse data and gain lot of insights on transactions, number of users, top 10 state, district, pincode and which brand has most number of users and so on. Bar charts, Pie charts and Geo map visualization are used to get some insights.")
    with col2:
        st.image("/Users/allen/Documents/Py VE/Includes/home.png")

elif selected == "Explore Data":
    tab1, tab2, tab3 = st.tabs(["#### Aggregated Analysis", "#### Map Analysis", "#### Top Analysis"])
    # Aggregrated Data
    with tab1:         
        method = st.radio("### :blue[Select The Method]",["Insurance Analysis", "Transaction Analysis", "User Analysis"],horizontal= True)
        # Aggregrated Insurance
        if method == "Insurance Analysis": 
            col1,col2 = st.columns(2,gap = 'large')
            with col1:           
                year = st.slider('#### Year',aggr_insurance.year.min(),aggr_insurance.year.max())
                q_check = st.toggle('Quarter View')
                if (q_check):
                        with col2:
                            quarter = st.slider("#### Quarter",1,4)        
            if(not q_check):
                dfyq_state(aggr_insurance,year,quarter = None)
            else:
                if(year == 2020) and (quarter == 1):
                    st.markdown(f"### :red[Sorry No Data to Display for {year} Quarter: {quarter}]")
                else:
                    dfyq_state(aggr_insurance,year,quarter) # Quarter is an optional parameter
                
        elif method == "Transaction Analysis":
            col1,col2 = st.columns(2,gap = 'large')
            with col1:           
                year = st.slider('#### Year',aggr_transaction.year.min(),aggr_transaction.year.max())
                q_check = st.toggle('Quarter View')
                if (q_check):
                        with col2:
                            quarter = st.slider("#### Quarter",1,4)   
            if (not q_check):
                dfyq_state(aggr_transaction,year)
                col1,col2= st.columns(2)            
                with col1:
                    states = aggr_transaction['state'].unique()
                    states.sort()  # To get state names is ascending order
                    state = st.selectbox("Select The State",states)
                dfyqs_ttype(aggr_transaction,year,state)
            else:
                dfyq_state(aggr_transaction,year,quarter) # Quarter is an optional parameter
                col1,col2= st.columns(2)            
                with col1:
                    states = aggr_transaction['state'].unique()
                    states.sort()  # To get state names is ascending order
                    state = st.selectbox("Select The State ",states)
                dfyqs_ttype(aggr_transaction,year,state,quarter)
            
        elif method == "User Analysis":          
            col1,col2 = st.columns(2,gap = 'large')
            with col1:           
                year = st.slider('#### Year',aggr_user.year.min(),aggr_user.year.max())
                q_check = st.toggle('Quarter View')
                if (q_check):
                        with col2:
                            quarter = st.slider("#### Quarter",1,4)  
            if (not q_check):
                dfyqs_brands(aggr_user,year)
            else:
                if(year == 2022) and (quarter in [2,3,4]):
                    st.markdown(f"### :red[Sorry No Data to Display for {year} Quarter: {quarter}]")
                else:                    
                    dfyqs_brands(aggr_user,year,quarter)
                    col1,col2 = st.columns(2)
                    with col1:
                        states = aggr_user['state'].unique()
                        states.sort()  # To get state names is ascending order
                        state = st.selectbox("Select The State ",states)
                    dfyqs_brands(aggr_user,year,quarter,state)
            
                

    # Map 
    with tab2:
        method = st.radio("Select The Method " ,["Insurance Analysis", "Transaction Analysis", "User Analysis"])

        if method == "Insurance Analysis":
            col1,col2 = st.columns(2,gap = 'large')
            with col1:           
                year = st.slider('#### Year',map_insurance.year.min(),map_insurance.year.max(),key='Map')
                q_check = st.toggle('Quarter View ')
                if(q_check):
                    with col2:
                        quarter = st.slider("#### Quarter",1,4)  
            if(not q_check):
                dfyq_state(map_insurance,year)
                states = map_insurance['state'].unique()
                states.sort()  # To get state names is ascending order
                state = st.selectbox("Select The State to analyze",states)
                dfyqs_district(map_insurance,year,state)
            else:
                if(year == 2020) and (quarter == 1):
                    st.markdown(f"### :red[Sorry No Data to Display for {year} Quarter: {quarter}]")
                else:
                    dfyq_state(map_insurance,year,quarter) # Quarter is an optional parameter           
                    col1,col2= st.columns(2)            
                    with col1:
                        states = map_insurance['state'].unique()
                        states.sort()  # To get state names is ascending order
                        state = st.selectbox("Select The State to analyze ",states)
                    dfyqs_district(map_insurance,year,state,quarter)
                
        elif method == 'Transaction Analysis':
            col1,col2 = st.columns(2,gap = 'large')
            with col1:           
                year = st.slider('#### Year',map_transaction.year.min(),map_transaction.year.max(),key='Map')
                q_check = st.toggle('Quarter View ')
                if(q_check):
                    with col2:
                        quarter = st.slider("#### Quarter",1,4)
            if(not q_check):
                dfyq_state(map_transaction,year)         
                col1,col2= st.columns(2)            
                with col1:
                    states = map_transaction['state'].unique()
                    states.sort()  # To get state names is ascending order
                    state = st.selectbox("Select The State to analyze",states)
                dfyqs_district(map_transaction,year,state)
            
            else:
                dfyq_state(map_transaction,year,quarter) # Quarter is an optional parameter           
                col1,col2= st.columns(2)            
                with col1:
                    states = map_transaction['state'].unique()
                    states.sort()  # To get state names is ascending order
                    state = st.selectbox("Select The State to analyze ",states)
                dfyqs_district(map_transaction,year,state,quarter)
            
        elif method == 'User Analysis':
            col1,col2 = st.columns(2,gap = 'large')
            with col1:           
                year = st.slider('#### Year',map_user.year.min(),map_user.year.max(),key='Map')
                q_check = st.toggle('Quarter View ')
                if(q_check):
                    with col2:
                        quarter = st.slider("#### Quarter",1,4)
            if(not q_check):
                dfyq_state_user(map_user,year)            
                col1,col2= st.columns(2)            
                with col1:
                    states = map_user['state'].unique()
                    states.sort()  # To get state names is ascending order
                    state = st.selectbox("Select The State to analyze",states)
                dfyqs_district_user(map_user,year,state)
            else:
                dfyq_state_user(map_user,year,quarter) # Quarter is an optional parameter           
                col1,col2= st.columns(2)            
                with col1:
                    states = map_user['state'].unique()
                    states.sort()  # To get state names is ascending order
                    state = st.selectbox("Select The State to analyze ",states)
                dfyqs_district_user(map_user,year,state,quarter)

    with tab3:
        method = st.radio("Select The Method  " ,["Insurance Analysis", "Transaction Analysis", "User Analysis"])
        if method == 'Insurance Analysis':
            col1,col2 = st.columns(2,gap = 'large')
            with col1:           
                year = st.slider('#### Year', top_insurance.year.min(), top_insurance.year.max(),key = 'TopYear')
                q_check = st.toggle('Quarter View', key = 'TopToggle')
                if(q_check):
                    with col2:
                        quarter = st.slider("#### Quarter", 1, 4, key = 'TopQuarter')
            if(not q_check):
                dfyq_state(top_insurance,year)            
                col1,col2= st.columns(2)            
                with col1:
                    states = top_insurance['state'].unique()
                    states.sort()  # To get state names is ascending order
                    state = st.selectbox("Select The State to Analyze the Top Insurance Data",states)
                dfys_quarter(top_insurance,year,state) 
            else:
                col1,col2= st.columns(2)            
                with col1:
                    quarter = st.slider("Select The Quarter to Analyze the Top Insurance Data ",top_insurance['quarter'].min(),top_insurance['quarter'].max(),top_insurance.loc[top_insurance['year'] == year,'quarter'].min())
                dfyq_state(top_insurance,year,quarter) 
        
        elif method == 'Transaction Analysis':
            col1,col2 = st.columns(2,gap = 'large')
            with col1:           
                year = st.slider('#### Year', top_transaction.year.min(), top_transaction.year.max(),key = 'TopYear')
                q_check = st.toggle('Quarter View', key = 'TopToggle')
                if(q_check):
                    with col2:
                        quarter = st.slider("#### Quarter", 1, 4, key = 'TopQuarter')
            if(not q_check):
                dfyq_state(top_transaction,year)
                col1,col2= st.columns(2)            
                with col1:
                    states = top_transaction['state'].unique()
                    states.sort()  # To get state names is ascending order
                    state = st.selectbox("Select The State to Analyze the Top Insurance Data",states)
                dfys_quarter(top_transaction,year,state) 
            else:
                col1,col2= st.columns(2)            
                with col1:
                    quarter = st.slider("Select The Quarter to Analyze the Top Insurance Data ",top_transaction['quarter'].min(),top_transaction['quarter'].max(),top_transaction.loc[top_transaction['year'] == year,'quarter'].min())
                dfyq_state(top_transaction,year,quarter)
        elif method == 'User Analysis':
            col1,col2 = st.columns(2,gap = 'large')
            with col1:           
                year = st.slider('#### Year', top_transaction.year.min(), top_transaction.year.max(),key = 'TopYear')
                q_check = st.toggle('Quarter View', key = 'TopToggle')
                if(q_check):
                    with col2:
                        quarter = st.slider("#### Quarter", 1, 4, key = 'TopQuarter')
            if(not q_check):
                dfy_state_quarter(top_user,year) 
                col1,col2 = st.columns(2)
                with col1:
                    states = top_user['state'].unique()
                    states.sort()  # To get state names is ascending order
                    state = st.selectbox("Select The State to Analyze the Top Insurance Data",states)
                dfys_quarter_pincode(top_user,year,state)
            else:
                dfy_state_quarter(top_user,year,quarter)
                col1,col2 = st.columns(2)
                with col1:
                    states = top_user['state'].unique()
                    states.sort()  # To get state names is ascending order
                    state = st.selectbox("Select The State to Analyze the Top Insurance Data",states)
                dfys_quarter_pincode(top_user,year,state,quarter)

if selected == "Top Charts":
    st.markdown("## :orange[Top Charts]")
    Type = st.sidebar.selectbox("**Type**", ("Insurance", "Transactions", "Users"))
 
    st.info(
            """
            #### From this menu we can get insights like :
            - Overall ranking on a particular Year and Quarter.
            - Top 10 State, District, Pincode based on Total number of transaction and Total amount spent on phonepe.
            - Top 10 State, District, Pincode based on Total phonepe users and their app opening frequency.
            - Top 10 mobile brands and its percentage based on the how many people use phonepe.
            """,
            icon= "🔍")
# Top Insurance         
    if Type == "Insurance":
        year = st.sidebar.slider("Year", min_value=2020, max_value=2023)
        quarter = st.sidebar.slider("Quarter", min_value=1, max_value=4)
        if(year == 2020 and quarter == 1):
            st.markdown(f"### :red[Sorry No Data to Display for {year} Quarter: {quarter}]")
        else:
            col1,col2 = st.columns(2,gap="small")
            with col1:
                st.markdown("### :orange[State]")
                myCursor.execute(f"select state, sum(transaction_count) as Total_Transactions_Count, sum(transaction_amount) as Total from aggregrated_insurance where year = {year} and quarter = {quarter} group by state order by Total desc limit 10")
                df = pd.DataFrame(myCursor.fetchall(), columns=['State', 'Transactions_Count','Total_Amount'])
                fig = px.pie(df, values='Total_Amount',
                                names='State',
                                title='Top 10',
                                color_discrete_sequence=px.colors.sequential.Agsunset,
                                hover_data=['Transactions_Count'],
                                labels={'Transactions_Count':'Transactions_Count'})

                fig.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig,use_container_width=True)
                
            with col2:
                st.markdown("### :orange[District]")
                myCursor.execute(f"select district , sum(transaction_count) as Total_Count, sum(transaction_amount) as Total from map_insurance where year = {year} and quarter = {quarter} group by district order by Total desc limit 10")
                df = pd.DataFrame(myCursor.fetchall(), columns=['District', 'Transactions_Count','Total_Amount'])

                fig = px.pie(df, values='Total_Amount',
                                names='District',
                                title='Top 10',
                                color_discrete_sequence=px.colors.sequential.Agsunset,
                                hover_data=['Transactions_Count'],
                                labels={'Transactions_Count':'Transactions_Count'})

                fig.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig,use_container_width=True)
                
            with col1:
                st.markdown("### :orange[Pincode]")
                myCursor.execute(f"select pincode, sum(transaction_count) as Total_Transactions_Count, sum(transaction_amount) as Total from top_insurance where year = {year} and quarter = {quarter} group by pincode order by Total desc limit 10")
                df = pd.DataFrame(myCursor.fetchall(), columns=['Pincode', 'Transactions_Count','Total_Amount'])
                fig = px.pie(df, values='Total_Amount',
                                names='Pincode',
                                title='Top 10',
                                color_discrete_sequence=px.colors.sequential.Agsunset,
                                hover_data=['Transactions_Count'],
                                labels={'Transactions_Count':'Transactions_Count'})

                fig.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig,use_container_width=True)
        
        
# Top Charts - TRANSACTIONS    
    if Type == "Transactions":
        year = st.sidebar.slider("Year", min_value=2018, max_value=2023)
        quarter = st.sidebar.slider("Quarter", min_value=1, max_value=4)
        col1,col2 = st.columns(2)
        with col1:
            st.markdown("### :orange[State]")
            myCursor.execute(f"select state, sum(transaction_count) as Total_Transactions_Count, sum(transaction_amount) as Total from aggregrated_transaction where year = {year} and quarter = {quarter} group by state order by Total desc limit 10")
            df = pd.DataFrame(myCursor.fetchall(), columns=['State', 'Transactions_Count','Total_Amount'])
            fig = px.bar(df, x ='State', y ='Total_Amount',
                        title='Top 10',
                        color_discrete_sequence=px.colors.sequential.Burg,
                        hover_data=['Transactions_Count'],
                        labels={'Transactions_Count':'Transactions_Count'})
            st.plotly_chart(fig,use_container_width=True)
            
        with col2:
            st.markdown("### :orange[District]")
            myCursor.execute(f"select district , sum(transaction_count) as Total_Count, sum(transaction_amount) as Total from map_transaction where year = {year} and quarter = {quarter} group by district order by Total desc limit 10")
            df = pd.DataFrame(myCursor.fetchall(), columns=['District', 'Transactions_Count','Total_Amount'])

            fig = px.bar(df, x ='District', y ='Total_Amount',
                        title='Top 10',
                        color_discrete_sequence= px.colors.sequential.Burg_r,
                        hover_data=['Transactions_Count'],
                        labels={'Transactions_Count':'Transactions_Count'})

            st.plotly_chart(fig,use_container_width=True)
            
        with col1:
            st.markdown("### :orange[Pincode]")
            myCursor.execute(f"select pincode, sum(transaction_count) as Total_Transactions_Count, sum(transaction_amount) as Total from top_transaction where year = {year} and quarter = {quarter} group by pincode order by Total desc limit 10")
            df = pd.DataFrame(myCursor.fetchall(), columns=['Pincode', 'Transactions_Count','Total_Amount'])
            fig = px.pie(df, values='Total_Amount',
                        names='Pincode',
                        title='Top 10',
                        color_discrete_sequence=px.colors.sequential.Agsunset,
                        hover_data=['Transactions_Count'],
                        labels={'Transactions_Count':'Transactions_Count'},hole= 0.5)

            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig,use_container_width=True)
        with col2:
            st.markdown("### :orange[Transaction Type]")
            myCursor.execute(f"select transaction_type,sum(transaction_count) as Total_Transactions_Count, sum(transaction_amount) as Total from aggregrated_transaction where year = {year} and quarter = {quarter} group by transaction_type order by total desc")
            df = pd.DataFrame(myCursor.fetchall(), columns = ['Tranasction_Type','Transactions_Count','Total_Amount'])
            fig = px.pie(df, values = 'Total_Amount', names ='Tranasction_Type', hole = 0.5,
                        hover_data= 'Transactions_Count',
                        color_discrete_sequence=px.colors.sequential.Agsunset)
            st.plotly_chart(fig)
            
    if Type == "Users":
        year = st.sidebar.slider("Year", min_value=2018, max_value=2023)
        quarter = st.sidebar.slider("Quarter", min_value=1, max_value=4)
        col1,col2 = st.columns(2,gap="small")
        
        with col1:
            st.markdown("### :orange[Brands]")
            if year in [2022,2023] and quarter in [2,3,4]:
                st.markdown(f"#### Sorry No Data to Display for {year} Quater: {quarter}")
            else:
                myCursor.execute(f"select brand, sum(transaction_count) as Total_Count, avg(percentage)*100 as Avg_Percentage from aggregrated_user where year = {year} and quarter = {quarter} group by brand order by Total_Count desc limit 10")
                df = pd.DataFrame(myCursor.fetchall(), columns=['Brand', 'Total_Users','Avg_Percentage'])
                fig = px.bar(df,
                            title='Top 10',
                            x="Total_Users",
                            y="Brand",
                            orientation='h',
                            color='Avg_Percentage',
                            color_continuous_scale=px.colors.sequential.Agsunset)
            st.plotly_chart(fig,use_container_width=True)   

        with col2:
            st.markdown("### :orange[District]")
            myCursor.execute(f"select district, sum(registered_users) as Total_Users, sum(app_opens) as Total_Appopens from map_user where year = {year} and quarter = {quarter} group by district order by Total_Users desc limit 10")
            df = pd.DataFrame(myCursor.fetchall(), columns=['District', 'Total_Users','Total_Appopens'])
            df.Total_Users = df.Total_Users.astype(float)
            fig = px.bar(df,
                         title='Top 10',
                         x="Total_Users",
                         y="District",
                         orientation='h',
                         color='Total_Users',
                         color_continuous_scale=px.colors.sequential.Agsunset)
            st.plotly_chart(fig,use_container_width=True)
            
        with col1:
            st.markdown("### :orange[State]")
            myCursor.execute(f"select state, sum(registered_users) as Total_Users, sum(app_opens) as Total_Appopens from map_user where year = {year} and quarter = {quarter} group by state order by Total_Users desc limit 10")
            df = pd.DataFrame(myCursor.fetchall(), columns=['State', 'Total_Users','Total_Appopens'])
            fig = px.pie(df, values='Total_Users',
                             names='State', hole= 0.5,
                             title='Top 10',
                             color_discrete_sequence=px.colors.sequential.Agsunset,
                             hover_data=['Total_Appopens'],
                             labels={'Total_Appopens':'Total_Appopens'})

            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig,use_container_width=True)
              
        with col2:
            st.markdown("### :orange[Pincode]")
            myCursor.execute(f"select pincode, sum(registered_users) as Total_Users from top_user where year = {year} and quarter = {quarter} group by pincode order by Total_Users desc limit 10")
            df = pd.DataFrame(myCursor.fetchall(), columns=['Pincode', 'Total_Users'])
            fig = px.pie(df,
                         values='Total_Users',
                         names='Pincode',hole= 0.5,
                         title='Top 10',
                         color_discrete_sequence=px.colors.sequential.Agsunset,
                         hover_data=['Total_Users'])
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig,use_container_width=True)
            
        
if selected == "About":
    col1,col2 = st.columns([3,3],gap="medium")
    with col1:
        st.write(" ")
        st.write(" ")
        st.markdown("### :violet[About PhonePe Pulse:] ")
        st.write("##### BENGALURU, India, On Sept. 3, 2021 PhonePe, India's leading fintech platform, announced the launch of PhonePe Pulse, India's first interactive website with data, insights and trends on digital payments in the country. The PhonePe Pulse website showcases more than 2000+ Crore transactions by consumers on an interactive map of India. With  over 45% market share, PhonePe's data is representative of the country's digital payment habits.")
        
        st.write("##### The insights on the website and in the report have been drawn from two key sources - the entirety of PhonePe's transaction data combined with merchant and customer interviews. The report is available as a free download on the PhonePe Pulse website and GitHub.")
        
        st.markdown("### :violet[About PhonePe:] ")
        st.write("##### PhonePe is India's leading fintech platform with over 300 million registered users. Using PhonePe, users can send and receive money, recharge mobile, DTH, pay at stores, make utility payments, buy gold and make investments. PhonePe forayed into financial services in 2017 with the launch of Gold providing users with a safe and convenient option to buy 24-karat gold securely on its platform. PhonePe has since launched several Mutual Funds and Insurance products like tax-saving funds, liquid funds, international travel insurance and Corona Care, a dedicated insurance product for the COVID-19 pandemic among others. PhonePe also launched its Switch platform in 2018, and today its customers can place orders on over 600 apps directly from within the PhonePe mobile app. PhonePe is accepted at 20+ million merchant outlets across Bharat")
        
        st.write("**:violet[My Project GitHub link]** ⬇️")
        st.write("")
        st.write("**:violet[Image and content source]** ⬇️")
        st.write("https://www.prnewswire.com/in/news-releases/phonepe-launches-the-pulse-of-digital-payments-india-s-first-interactive-geospatial-website-888262738.html")
        
    with col2:
        st.write(" ")
        st.write(" ")
        st.write(" ")
        st.write(" ")
        st.image("/Users/allen/Documents/Py VE/Includes/Pulseimg.jpg")
    
            