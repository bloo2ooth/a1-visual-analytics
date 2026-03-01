from bokeh.plotting import figure, show
from bokeh.layouts import row, column
from bokeh.models import ColumnDataSource, HoverTool, DateRangeSlider, Range1d
from bokeh.transform import dodge
from bokeh.io import curdoc
from datetime import timedelta
from preprocessing import preprocess_sales_data, preprocess_review_crash_data, get_sales_volume
import pandas as pd


df_reviews_crash_data = preprocess_review_crash_data()

source = ColumnDataSource(df_reviews_crash_data)

fig1 = figure(
    title="Star Rating vs Daily Crashes",
    width=600,
    height=300,
    x_range=Range1d(0, 5 + 0.5),
    y_range=Range1d(0, df_reviews_crash_data["Daily Crashes"].max() + 5)
)
fig1.scatter(x='avg_rating', y='Daily Crashes', source=source, size=8, color='red', alpha=0.7)
fig1.xaxis.axis_label = 'Average Star Rating'
fig1.yaxis.axis_label = 'Number of Daily Crashes'

date_range = DateRangeSlider(
    title="Select Date Range",
    start=df_reviews_crash_data["Date"].min(),
    end=df_reviews_crash_data["Date"].max(),
    value=(df_reviews_crash_data["Date"].min(), df_reviews_crash_data["Date"].max()),
    step=1
)

hover1 = HoverTool()
hover1.tooltips=[
    ('Date', '@Date{%F}'),
    ('Average Star Rating', '@{avg_rating}'),
    ('Number of Reviews', '@{review_count}'),
    ('Daily Crashes', '@{Daily Crashes}')
]

hover1.formatters = {
    '@Date': 'datetime'
}
fig1.add_tools(hover1)

def update_rating_crash_plot(attr, old, new):
    start, end = date_range.value
    filtered = df_reviews_crash_data[
        (df_reviews_crash_data["Date"] >= pd.to_datetime(start, unit='ms')) &
        (df_reviews_crash_data["Date"] <= pd.to_datetime(end, unit='ms'))
    ]

    source.data = filtered.to_dict('list') 

date_range.on_change("value", update_rating_crash_plot)

# monthly sales #
df_monthly_sales = get_sales_volume()
source = ColumnDataSource(df_monthly_sales)

fig2 = figure(
    title="Monthly Sales Volume and Transaction/Refund Count",
    width=800,
    height=400,
    x_axis_type="datetime"
)
fig2.vbar(x=dodge('Month', -1, range=fig2.x_range),width=timedelta(days=4), top='sales_volume', source=source, color='red')
fig2.vbar(x=dodge('Month', -1, range=fig2.x_range), width=timedelta(days=4), top='num_transactions', source=source, color='blue')
fig2.vbar(x=dodge('Month', 1.15, range=fig2.x_range), width=timedelta(days=4), top='num_refunds', source=source, color='green')
fig2.xaxis.axis_label = 'Month'
fig2.yaxis.axis_label = 'Monthly Sales Volume in EUR'

hover2 = HoverTool()
hover2.tooltips=[
    ('Month and Year', '@Month{%B-%Y}'),
    ('Monthly Sale Volume', '@{sales_volume}'),
    ('Number of Transactions', '@{num_transactions}'),
    ('Number of Refunds', '@{num_refunds}')
]
hover2.formatters = {
    '@Month': 'datetime'
}

fig2.add_tools(hover2)


layout = row(column(date_range, fig1), column(fig2))

curdoc().add_root(layout)
