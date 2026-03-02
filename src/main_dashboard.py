from bokeh.plotting import figure, show
from bokeh.layouts import row, column
from bokeh.models import ColumnDataSource, HoverTool, DateRangeSlider, Range1d, LinearColorMapper, GeoJSONDataSource, DateSlider, LinearAxis
from bokeh.palettes import Viridis256
from bokeh.transform import dodge
from bokeh.io import curdoc
from datetime import timedelta
from preprocessing import preprocess_review_crash_data, get_sales_volume, get_world_daily_sales
import pandas as pd


df_reviews_crash_data = preprocess_review_crash_data()

source1 = ColumnDataSource(df_reviews_crash_data)

fig1 = figure(
    title="Star Rating vs Daily Crashes",
    width=600,
    height=300,
    x_range=Range1d(0, 5 + 0.5),
    y_range=Range1d(0, df_reviews_crash_data["Daily Crashes"].max() + 5)
)
fig1.scatter(x='avg_rating', y='Daily Crashes', source=source1, size=8, color='red', alpha=0.7)
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

    source1.data = filtered.to_dict('list') 

date_range.on_change("value", update_rating_crash_plot)

# monthly sales #
df_monthly_sales = get_sales_volume()
source2 = ColumnDataSource(df_monthly_sales)

fig2 = figure(
    title="Monthly Sales Volume and Transaction/Refund Count",
    width=800,
    height=400,
    x_axis_type="datetime"
)
fig2.xaxis.axis_label = 'Month'
fig2.yaxis.axis_label = 'Monthly Sales Volume in EUR'
# add a seperate y functions for refund due to different dimensions
fig2.y_range = Range1d(start=0, end=df_monthly_sales['sales_volume'].max())
fig2.extra_y_ranges = {"refund": Range1d(start=0, end=df_monthly_sales['num_refunds'].max()+1)}
fig2.add_layout(LinearAxis(y_range_name="refund", axis_label="Number of Refunds"), 'right')

fig2.vbar(x=dodge('Month', -1, range=fig2.x_range),width=timedelta(days=4), top='sales_volume', source=source2, color='red')
fig2.vbar(x=dodge('Month', -1, range=fig2.x_range), width=timedelta(days=4), top='num_transactions', source=source2, color='blue')
fig2.line(x='Month', y='num_refunds', y_range_name='refund', source=source2, color='green')


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


df_world_sales = get_world_daily_sales()
df_world_sales_json = df_world_sales.copy()
df_world_sales_json['Transaction Date'] = df_world_sales['Transaction Date'].dt.strftime("%Y-%m-%d")
source3 = GeoJSONDataSource(
    geojson=df_world_sales_json.to_json()
)

fig3 = figure(
    title="Monthly Sales Volume and Transaction/Refund Count",
    width=800,
    height=400,
    x_axis_type="datetime"
)
# create color map
color_mapper = LinearColorMapper(
    palette=Viridis256,
    low=df_world_sales.sales_volume.min(),
    high=df_world_sales.sales_volume.max()
)
fig3.patches(
    'xs',
    'ys',
    source=source3,
    fill_color={'field': 'sales_volume', 'transform': color_mapper},
    line_color='gray',
    line_width=0.5
)
date_slider_world = DateSlider(
    title="Select Date",
    start=df_world_sales["Transaction Date"].min(),
    end=df_world_sales["Transaction Date"].max(),
    value=df_world_sales["Transaction Date"].min(),
    step=1
)

def update_world_sales_plot(attr, old, new):
    date = date_slider_world.value
    filtered = df_world_sales[(df_world_sales["Transaction Date"] == pd.to_datetime(date, unit='ms')) ]
    filtered['Transaction Date'] = filtered['Transaction Date'].dt.strftime("%Y-%m-%d")
    source3.geojson = filtered.to_json()

date_slider_world.on_change("value", update_world_sales_plot)

layout = row(column(date_range, fig1), column(fig2, date_slider_world, fig3))

curdoc().add_root(layout)
