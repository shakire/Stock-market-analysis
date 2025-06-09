SELECT * FROM stockmarket.stock_market;
select * from stock_market where Ticker = 'SBIN';

#creating yearly returns
select Ticker, Year(Date) as year, min(Date) as first_date, max(Date) as last_date from stock_market group by Ticker,Year(Date);

#Top 10 Green stocks
select bounds.Ticker,bounds.year,s_open.open as start_open,s_close.close as end_close,
round((s_close.close - s_open.open) / s_open.open * 100, 2) as yearly_return_percent
from(
select Ticker, Year(Date) as year, min(Date) as first_date, max(Date) as last_date from stock_market group by Ticker,Year(Date)) as bounds
join stock_market s_open 
on s_open.Ticker = bounds.Ticker and s_open.Date = bounds.first_date
join stock_market s_close 
on s_close.Ticker = bounds.Ticker and s_close.Date = bounds.last_date
order by yearly_return_percent desc limit 10;

#Top 10 Red stocks
select bounds.Ticker,bounds.year,s_open.open as start_open,s_close.close as end_close,
round((s_close.close - s_open.open) / s_open.open * 100, 2) as yearly_return_percent
from(
select Ticker, Year(Date) as year, min(Date) as first_date, max(Date) as last_date from stock_market group by Ticker,Year(Date)) as bounds
join stock_market s_open 
on s_open.Ticker = bounds.Ticker and s_open.Date = bounds.first_date
join stock_market s_close 
on s_close.Ticker = bounds.Ticker and s_close.Date = bounds.last_date
order by yearly_return_percent asc limit 10; 

#Total number of green stocks and red stocks
with yearly_returns as (select bounds.Ticker,bounds.year,
round((s_close.close - s_open.open) / s_open.open * 100, 2) as yearly_return_percent
from(
select Ticker, Year(Date) as year, min(Date) as first_date, max(Date) as last_date from stock_market group by Ticker,Year(Date)) as bounds
join stock_market s_open 
on s_open.Ticker = bounds.Ticker and s_open.Date = bounds.first_date
join stock_market s_close 
on s_close.Ticker = bounds.Ticker and s_close.Date = bounds.last_date)
select 
sum(yearly_return_percent>0)as green_stocks,
sum(yearly_return_percent<0)as red_stocks from yearly_returns;

#average price across all stocks.
select avg(close) as average_price from stock_market;

#average Volume across all stocks.
select avg(volume) as average_price from stock_market;






   


