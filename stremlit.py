import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import mysql.connector
from mysql.connector import Error


host = "localhost"
user = "root"
password = "tonystark"
database = "stockmarket"

st.title("Stock Data Analysis")
st.header("Stock Performance")

def check_connection():
    
    try:
        
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        if conn.is_connected():
            st.write("Connection to the database is successful!")
        else:
            st.write("Failed to connect to the database.")
    except Error as e:
        st.error(f"Error connecting to the database: {e}")
    finally:
        if conn.is_connected():
            conn.close()

check_connection()
def execute_query(query):
    
    try:
        
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        if conn.is_connected():
           
            df = pd.read_sql(query, conn)
            return df
    except Error as e:
        st.error(f"Error connecting to the database: {e}")
        return pd.DataFrame()  
    finally:
        if conn.is_connected():
            conn.close()

menu_options = ["select an option",
                "Top 10 Green Stocks",
                "Top 10 Loss Stocks",
                "overall number of green vs. red stocks",
                "average price across all stocks",
                "average Volume across all stocks",
                "Volatility Analysis",
                "Cumulative Return Over Time",
                "Sector-wise Performance",
                "Stock Price Correlation",
                "Top 5 Gainers and Losers (Month-wise)"]

selected_option = st.selectbox("Choose a query to run:", menu_options)

Top_10_green = """select bounds.Ticker,bounds.year,s_open.open as start_open,s_close.close as end_close,
                round((s_close.close - s_open.open) / s_open.open * 100, 2) as yearly_return_percent
                from(
                select Ticker, Year(Date) as year, min(Date) as first_date, max(Date) as last_date from stock_market group by Ticker,Year(Date)) as bounds
                join stock_market s_open 
                on s_open.Ticker = bounds.Ticker and s_open.Date = bounds.first_date
                join stock_market s_close 
                on s_close.Ticker = bounds.Ticker and s_close.Date = bounds.last_date
                order by yearly_return_percent desc limit 10;"""
if selected_option == "Top 10 Green Stocks":
     st.info("Fetching data...")
     result_data = execute_query(Top_10_green)
     if not result_data.empty:
        st.table(result_data)
     else:
        st.warning("No data found.")

Top_10_red = """select bounds.Ticker,bounds.year,s_open.open as start_open,s_close.close as end_close,
                round((s_close.close - s_open.open) / s_open.open * 100, 2) as yearly_return_percent
                from(
                select Ticker, Year(Date) as year, min(Date) as first_date, max(Date) as last_date from stock_market group by Ticker,Year(Date)) as bounds
                join stock_market s_open 
                on s_open.Ticker = bounds.Ticker and s_open.Date = bounds.first_date
                join stock_market s_close 
                on s_close.Ticker = bounds.Ticker and s_close.Date = bounds.last_date
                order by yearly_return_percent asc limit 10;"""
if selected_option == "Top 10 Loss Stocks":
     st.info("Fetching data...")
     result_data = execute_query(Top_10_red)
     if not result_data.empty:
        st.table(result_data)
     else:
        st.warning("No data found.")

total_green_red = """with yearly_returns as (select bounds.Ticker,bounds.year,
                    round((s_close.close - s_open.open) / s_open.open * 100, 2) as yearly_return_percent
                    from(
                    select Ticker, Year(Date) as year, min(Date) as first_date, max(Date) as last_date from stock_market group by Ticker,Year(Date)) as bounds
                    join stock_market s_open 
                    on s_open.Ticker = bounds.Ticker and s_open.Date = bounds.first_date
                    join stock_market s_close 
                    on s_close.Ticker = bounds.Ticker and s_close.Date = bounds.last_date)
                    select 
                    sum(yearly_return_percent>0)as green_stocks,
                    sum(yearly_return_percent<0)as red_stocks from yearly_returns;"""
if selected_option == "overall number of green vs. red stocks":
     st.info("Fetching data...")
     result_data = execute_query(total_green_red)
     if not result_data.empty:
        st.table(result_data)
     else:
        st.warning("No data found.")

Average_price = """select avg(close) as average_price from stock_market;"""
if selected_option == "average price across all stocks":
     st.info("Fetching data...")
     result_data = execute_query(Average_price)
     if not result_data.empty:
        st.table(result_data)
     else:
        st.warning("No data found.")

volume = """select avg(volume) as average_price from stock_market;"""
if selected_option == "average Volume across all stocks":
     st.info("Fetching data...")
     result_data = execute_query(volume)
     if not result_data.empty:
        st.table(result_data)
     else:
        st.warning("No data found.")

df_volatility = pd.read_csv("C:\\Data science\\Project 2 - data driven stock analysis\\project\\volatility.csv")  

if selected_option == "Volatility Analysis":
    top_10_volatility = df_volatility.sort_values(by="volatility", ascending=False).head(10)
    st.dataframe(top_10_volatility)
    fig = px.bar(top_10_volatility, x="Ticker", y="volatility", color="Ticker",
                 title="Top 10 Volatile Stocks")
    st.plotly_chart(fig, use_container_width=True)

df_cumulative = pd.read_csv("C:\\Data science\\Project 2 - data driven stock analysis\\project\\top_5_cumulative_return.csv")

if selected_option == "Cumulative Return Over Time":
   df = pd.read_csv("cleaned.csv")
   df["Date"] = pd.to_datetime(df["Date"])
   df["daily returns"] = df.groupby("Ticker")["close"].pct_change()
   df["daily returns"] = df["daily returns"].fillna(0)
   df["cumulative return"] = (1 + df["daily returns"]).groupby(df["Ticker"]).cumprod() - 1
   df_cumulative = df.groupby("Ticker")["cumulative return"].last()
   cumulative_return = df_cumulative.sort_values(ascending=False).head(5)
   cumulative_return_df = cumulative_return.reset_index()
   st.subheader("Top 5 Performing Stocks by Cumulative Return")
   st.dataframe(cumulative_return_df)
   fig, ax = plt.subplots(figsize=(12, 6))
   
   for ticker in cumulative_return.index:  # use the index since it's a Series
    data = df[df["Ticker"] == ticker]
    ax.plot(data["Date"], data["cumulative return"], label=ticker)

    ax.set_title("Cumulative Return for Top 5 Performing Stocks")
    ax.set_xlabel("Date")
    ax.set_ylabel("Cumulative Return")
    ax.legend(title="Ticker")
    
    st.pyplot(fig)

df_cleaned = pd.read_csv('C:\\Data science\\Project 2 - data driven stock analysis\\project\\cleaned.csv')
df_sector = pd.read_csv('C:\\Data science\\Project 2 - data driven stock analysis\\Sector_data - Sheet1.csv')

if selected_option == "Sector-wise Performance":
    df_cleaned.columns = df_cleaned.columns.str.strip()
    df_sector.columns = df_sector.columns.str.strip()
    df_sector['Ticker'] = df_sector['Symbol'].str.split(':').str[-1].str.strip()
    df_final = df_cleaned.merge(df_sector[['Ticker', 'sector']], on='Ticker', how='left')
    df_final["Date"] = pd.to_datetime(df_final["Date"])
    df_final["daily returns"] = df_final.groupby("Ticker")["close"].pct_change().fillna(0)
    df_return = df_final.groupby("sector")["daily returns"].std().reset_index()
    df_return = df_return.sort_values(by="daily returns", ascending=False)
    st.subheader("Sector-wise Daily Return Volatility")
    st.dataframe(df_return)
    fig, ax = plt.subplots(figsize=(15, 6))
    ax.bar(df_return["sector"], df_return["daily returns"], color='skyblue')
    ax.set_title("Sector-wise Performance (Volatility)")
    ax.set_xlabel("Sector")
    ax.set_ylabel("Daily Returns Std Dev")
    ax.set_xticklabels(df_return["sector"], rotation=90)
    ax.grid(True)
    st.pyplot(fig)


if selected_option == "Stock Price Correlation":
    df_final = pd.read_csv("C:\\Data science\\Project 2 - data driven stock analysis\\project\\cleaned.csv")
    df_final["Date"] = pd.to_datetime(df_final["Date"])
    df_final.columns = df_final.columns.str.strip()
    df_pivot = df_final.pivot(index="Date", columns="Ticker", values="close")
    correlation_matrix = df_pivot.pct_change().corr()
    st.subheader("Stock Correlation Heatmap")
    fig, ax = plt.subplots(figsize=(20, 16))
    sns.heatmap(
        correlation_matrix,
        annot=True,
        cmap="coolwarm",
        annot_kws={"size": 6},
        linewidths=0.5,
        cbar=True,
        square=True,
        ax=ax
    )
    ax.set_title("Stock Correlation")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=90)
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0)
    plt.tight_layout()
    st.pyplot(fig)

df_cleaned = pd.read_csv('C:\\Data science\\Project 2 - data driven stock analysis\\project\\cleaned.csv')
df_sector = pd.read_csv('C:\\Data science\\Project 2 - data driven stock analysis\\Sector_data - Sheet1.csv')
df_cleaned.columns = df_cleaned.columns.str.strip()
df_sector.columns = df_sector.columns.str.strip()
df_sector['Ticker'] = df_sector['Symbol'].str.split(':').str[-1].str.strip()
df_final = df_cleaned.merge(df_sector[['Ticker', 'sector']], on='Ticker', how='left')
df_final['Date'] = pd.to_datetime(df_final['Date'])
if selected_option == "Top 5 Gainers and Losers (Month-wise)":
    monthly_returns = {}
    for ticker in df_final['Ticker'].unique():
        ticker_df = df_final[df_final['Ticker'] == ticker].copy()
        ticker_df = ticker_df.set_index('Date').sort_index()
        monthly_price = ticker_df['close'].resample('M').last()
        monthly_return = monthly_price.pct_change() * 100
        monthly_returns[ticker] = monthly_return

    monthly_df = pd.DataFrame(monthly_returns).dropna(how='all')
    monthly_df.index.name = 'Month'
    monthly_df = monthly_df.round(2)

    # 4. Find top gainers/losers for each month
    top_movers = {}
    for month in monthly_df.index:
        month_returns = monthly_df.loc[month].dropna()
        top_gainers = month_returns.sort_values(ascending=False).head(5)
        top_losers = month_returns.sort_values().head(5)
        top_movers[month.strftime('%b %Y')] = {
            'Top Gainers': top_gainers,
            'Top Losers': top_losers
        }

    # 5. Prepare months in order (for plotting)
    from datetime import datetime
    month_dt_pairs = [(datetime.strptime(m, "%b %Y"), m) for m in top_movers.keys()]
    month_dt_pairs.sort()
    months = [m[1] for m in month_dt_pairs]  # all 14 months

    # 6. Plotting 14 months (7 rows x 2 columns)
    fig, axes = plt.subplots(nrows=7, ncols=2, figsize=(18, 35))
    axes = axes.flatten()

    for i, month in enumerate(months):
        ax = axes[i]
        gainers = top_movers[month].get('Top Gainers', pd.Series())
        losers = top_movers[month].get('Top Losers', pd.Series())
        gainers = gainers[::-1]
        losers = losers[::-1]
        combined = pd.concat([losers, gainers])
        colors = ['red'] * len(losers) + ['green'] * len(gainers)
        if not combined.empty:
            combined.plot(kind='barh', color=colors, ax=ax)
            ax.set_title(f"{month}: Top 5 Gainers & Losers", fontsize=10)
            ax.set_xlabel('Monthly Return (%)')
            ax.grid(True, axis='x', linestyle='--', linewidth=0.5)
            min_val = combined.min() * 1.1
            max_val = combined.max() * 1.1
            ax.set_xlim(min(-10, min_val), max(10, max_val))
        else:
            ax.set_visible(False)

    # Hide any unused axes (if less than 14)
    for j in range(len(months), len(axes)):
        fig.delaxes(axes[j])

    plt.tight_layout()
    plt.suptitle("Top 5 Monthly Gainers & Losers (Based on Percentage Return)", fontsize=16, y=1.02)
    plt.subplots_adjust(top=0.95)
    st.subheader("Top 5 Monthly Gainers & Losers")
    st.pyplot(fig)

