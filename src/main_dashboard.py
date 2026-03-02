from bokeh.plotting import figure, show
from bokeh.layouts import row, column
from bokeh.models import ColumnDataSource, HoverTool, DateRangeSlider, Range1d, LinearColorMapper, GeoJSONDataSource, DateSlider, LinearAxis, ColorBar, Select
from bokeh.palettes import Viridis256, RdYlGn11
from bokeh.transform import dodge
from bokeh.io import curdoc
from datetime import timedelta
from preprocessing import preprocess_review_crash_data, get_sales_volume, get_world_daily_sales, get_sales_by_sku
import pandas as pd


df_reviews_crash_data, df_ratings_country = preprocess_review_crash_data()  

source1 = ColumnDataSource(df_reviews_crash_data)

fig1 = figure(
    title="Star Rating vs Daily Crashes",
    width=700,
    height=300,
    x_range=Range1d(0, 5 + 0.5),
    y_range=Range1d(0, df_reviews_crash_data["Daily Crashes"].max() + 5),
    sizing_mode="stretch_width"
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
    ('Daily Crashes', '@{Daily Crashes}'),
    ('Daily ANRs', '@{Daily ANRs}')    
]
hover1.formatters = {
    '@Date': 'datetime'
}
fig1.add_tools(hover1)
# crashes and ANRs over time 
fig1b = figure(                                                                     
    title="Daily Crashes and ANRs over Time",                                       
    height=250,                                                                     
    width=700,                                                                      
    x_axis_type="datetime", sizing_mode="stretch_width"                                                          
)                                                                                   
fig1b.line(x='Date', y='Daily Crashes', source=source1,                            
           color='red', legend_label="Crashes")                                     
fig1b.line(x='Date', y='Daily ANRs', source=source1,                               
           color='orange', legend_label="ANRs")                                     
fig1b.xaxis.axis_label = 'Date'                                                    
fig1b.yaxis.axis_label = 'Count'                                                   
fig1b.legend.click_policy = "hide"         
# add secondary y axis for review count
fig1b.extra_y_ranges = {"reviews": Range1d(start=0, end=df_reviews_crash_data['review_count'].max() + 5)}
fig1b.add_layout(LinearAxis(y_range_name="reviews", axis_label="Review Count"), 'right')
fig1b.line(x='Date', y='review_count', y_range_name='reviews', source=source1,
           color='purple', legend_label="Review Count", line_dash='dashed')
hover1b = HoverTool()
hover1b.tooltips = [
    ('Date', '@Date{%F}'),
    ('Daily Crashes', '@{Daily Crashes}'),
    ('Daily ANRs', '@{Daily ANRs}')
]
hover1b.formatters = {'@Date': 'datetime'}
fig1b.add_tools(hover1b)

def update_rating_crash_plot(attr, old, new):
    start, end = date_range.value
    start_dt = pd.to_datetime(start, unit='ms')
    end_dt   = pd.to_datetime(end, unit='ms')

    # filter scatter/time series data
    filtered = df_reviews_crash_data[
        (df_reviews_crash_data["Date"] >= start_dt) &
        (df_reviews_crash_data["Date"] <= end_dt)
    ]
    source1.data = filtered.to_dict('list')

    # also filter sku chart by same date range
    filtered_sku = df_sku[
        (df_sku["Month"] >= start_dt) &
        (df_sku["Month"] <= end_dt)
    ]
    source4_premium.data   = filtered_sku[filtered_sku['Sku Id'] == 'premium'].to_dict('list')
    source4_character.data = filtered_sku[filtered_sku['Sku Id'] == 'unlockcharactermanager'].to_dict('list')

date_range.on_change("value", update_rating_crash_plot)

# monthly sales #
df_monthly_sales = get_sales_volume()
source2 = ColumnDataSource(df_monthly_sales)

fig2 = figure(
    title="Monthly Sales Volume and Transaction/Refund Count",
    width=700,
    height=400,
    x_axis_type="datetime", sizing_mode="stretch_width"
)
fig2.xaxis.axis_label = 'Month'
fig2.yaxis.axis_label = 'Monthly Sales Volume in EUR'
# add a seperate y functions for refund due to different dimensions
fig2.y_range = Range1d(start=0, end=df_monthly_sales['sales_volume'].max())
fig2.extra_y_ranges = {"refund": Range1d(start=0, end=df_monthly_sales['num_refunds'].max()+1)}
fig2.add_layout(LinearAxis(y_range_name="refund", axis_label="Number of Refunds"), 'right')

fig2.vbar(x=dodge('Month', -1, range=fig2.x_range),width=timedelta(days=4), top='sales_volume', source=source2, color='red', legend_label="Sales Volume")
fig2.vbar(x=dodge('Month', 100000000, range=fig2.x_range), width=timedelta(days=4), top='num_transactions', source=source2, color='blue', legend_label="Transactions")
fig2.line(x='Month', y='num_refunds', y_range_name='refund', source=source2, color='green', legend_label="Refunds")
fig2.legend.click_policy = "hide"

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
# prepare ratings per country for map overlay   
df_ratings_country["Date"] = pd.to_datetime(df_ratings_country["Date"])
df_ratings_agg = df_ratings_country.groupby("Country").agg(
    avg_rating=("Daily Average Rating", "mean")
).reset_index()
# merge average ratings into world sales for geographic display     
df_world_sales = df_world_sales.merge(
    df_ratings_agg, left_on="ISO_A2", right_on="Country", how="left"
)

df_world_sales_json = df_world_sales.copy()
df_world_sales_json['Transaction Date'] = df_world_sales['Transaction Date'].dt.strftime("%Y-%m-%d")
source3 = GeoJSONDataSource(
    geojson=df_world_sales_json.to_json()
)
# allow management to toggle between sales volume and average rating                
map_metric_select = Select(                                                         
    title="Map Metric",                                                             
    value="sales_volume",                                                           
    options=[("sales_volume", "Sales Volume (EUR)"),                               
             ("avg_rating", "Average Rating")]                                      
)                                                                                   
fig3 = figure(
    title="World Map Sales Volume Visualization",
    width=700,
    height=400, sizing_mode="stretch_width"
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
# add legend for colormap 
color_bar = ColorBar(color_mapper=color_mapper, label_standoff=12, location=(0,0), title="Sales Volume")

fig3.add_layout(color_bar, 'right')
# add hover showing both sales and rating per country                               
hover3 = HoverTool()                                                                
hover3.tooltips = [                                                                 
    ('Country', '@SOVEREIGNT'),                                                     
    ('Sales Volume', '@sales_volume{0.00}'),                                        
    ('Transactions', '@num_transactions'),                                          
    ('Avg Rating', '@avg_rating{0.00}')                                             
]                                                                                   
fig3.add_tools(hover3)                                                              

def update_world_sales_plot(attr, old, new):
    date = date_slider_world.value
    filtered = df_world_sales[(df_world_sales["Transaction Date"] == pd.to_datetime(date, unit='ms')) ]
    filtered['Transaction Date'] = filtered['Transaction Date'].dt.strftime("%Y-%m-%d")
    source3.geojson = filtered.to_json()

date_slider_world.on_change("value", update_world_sales_plot)

# update color mapper when metric selection changes                                 
def update_map_metric(attr, old, new):                                             
    metric = map_metric_select.value                                                
    color_mapper.low  = df_world_sales[metric].min()                               
    color_mapper.high = df_world_sales[metric].max()                               
    # update patches to use selected metric field                                   
    fig3.renderers[0].glyph.fill_color = {'field': metric,'transform': color_mapper}              
    color_bar.title = "Sales Volume (EUR)" if metric == "sales_volume" else "Avg Rating"  

map_metric_select.on_change("value", update_map_metric)                            

df_sku = get_sales_by_sku()
source4_premium = ColumnDataSource(df_sku[df_sku['Sku Id'] == 'premium'])
source4_character = ColumnDataSource(df_sku[df_sku['Sku Id'] == 'unlockcharactermanager'])

fig4 = figure(
    title="Monthly Sales Volume split by Sku ID",
    width=700,
    height=400,
    x_axis_type="datetime", sizing_mode="stretch_width"
)
fig4.xaxis.axis_label = 'Month'
fig4.yaxis.axis_label = 'Monthly Sales Volume in EUR'
fig4.y_range = Range1d(start=0, end=df_monthly_sales['sales_volume'].max())

fig4.vbar(x=dodge('Month', -3 * 86400000, range=fig4.x_range),
          width=timedelta(days=4), top='revenue',
          source=source4_premium, color='red', legend_label="Premium")
fig4.vbar(x=dodge('Month', 3 * 86400000, range=fig4.x_range),
          width=timedelta(days=4), top='revenue',
          source=source4_character, color='blue', legend_label="Character Manager")

hover4 = HoverTool()
hover4.tooltips=[
    ('Month and Year', '@Month{%B-%Y}'),
    ('Monthly Sale Volume', '@{revenue}'),
    ('Number of Transactions', '@{transactions}')
]
hover4.formatters = {
    '@Month': 'datetime'
}

fig4.add_tools(hover4)

layout = row(
    column(fig4, date_range, fig1, fig1b),
    column(fig2, map_metric_select, date_slider_world, fig3), sizing_mode="stretch_width"
)

curdoc().add_root(layout)
