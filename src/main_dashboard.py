from bokeh.plotting import figure, show
from bokeh.layouts import row, column
from bokeh.models import ColumnDataSource, HoverTool, DateRangeSlider, Range1d
from bokeh.io import curdoc
from preprocessing import preprocess_sales_data, preprocess_review_crash_data, get_sales_volume
import pandas as pd
df_reviews_crash_data = preprocess_review_crash_data()

source = ColumnDataSource(df_reviews_crash_data)

fig = figure(
    title="Star Rating vs Daily Crashes",
    width=800,
    height=400,
    x_range=Range1d(0, 5 + 0.5),
    y_range=Range1d(0, df_reviews_crash_data["Daily Crashes"].max() + 5)
)
fig.scatter(x='avg_rating', y='Daily Crashes', source=source, size=8, color='red', alpha=0.7)
fig.xaxis.axis_label = 'Average Star Rating'
fig.yaxis.axis_label = 'Number of Daily Crashes'

date_range = DateRangeSlider(
    title="Select Date Range",
    start=df_reviews_crash_data["Date"].min(),
    end=df_reviews_crash_data["Date"].max(),
    value=(df_reviews_crash_data["Date"].min(), df_reviews_crash_data["Date"].max()),
    step=1
)

hover = HoverTool()
hover.tooltips=[
    ('Date', '@Date{%F}'),
    ('Average Star Rating', '@{avg_rating}'),
    ('Number of Reviews', '@{review_count}'),
    ('Daily Crashes', '@{Daily Crashes}')
]
fig.add_tools(hover)

hover.formatters = {
    '@Date': 'datetime'
}

def update_rating_crash_plot(attr, old, new):
    start, end = date_range.value
    filtered = df_reviews_crash_data[
        (df_reviews_crash_data["Date"] >= pd.to_datetime(start, unit='ms')) &
        (df_reviews_crash_data["Date"] <= pd.to_datetime(end, unit='ms'))
    ]

    source.data = filtered.to_dict('list') 

date_range.on_change("value", update_rating_crash_plot)

layout = column(date_range, fig)

curdoc().add_root(layout)