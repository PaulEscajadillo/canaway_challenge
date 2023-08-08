import streamlit as st
import datetime
import pandas as pd
import matplotlib.pyplot as plt

from streamlit_echarts import st_echarts
def render_pie_simple():
    options = {
        "title": {"text": "某站点用户访问来源", "subtext": "纯属虚构", "left": "center"},
        "tooltip": {"trigger": "item"},
        "legend": {"orient": "vertical", "left": "left",},
        "series": [
            {
                "name": "访问来源",
                "type": "pie",
                "radius": "50%",
                "data": [
                    {"value": 1048, "name": "搜索引擎"},
                    {"value": 735, "name": "直接访问"},
                    {"value": 580, "name": "邮件营销"},
                    {"value": 484, "name": "联盟广告"},
                    {"value": 300, "name": "视频广告"},
                ],
                "emphasis": {
                    "itemStyle": {
                        "shadowBlur": 10,
                        "shadowOffsetX": 0,
                        "shadowColor": "rgba(0, 0, 0, 0.5)",
                    }
                },
            }
        ],
    }
    st_echarts(
        options=options, height="600px",
    )
render_pie_simple()


st.header("Ventas")

cycles = pd.read_csv("data/cycles.csv")
#cycles.shape
cycles = cycles.loc[cycles.Group == 'sales_group1']
#cycles

cycles.Start = cycles.Start.apply(lambda x: datetime.datetime.strptime(x, '%m/%d/%Y').date())
cycles.End = cycles.End.apply(lambda x: datetime.datetime.strptime(x, '%m/%d/%Y').date())
cycles.Comparison_Start = cycles.Comparison_Start.apply(lambda x: datetime.datetime.strptime(x, '%m/%d/%Y').date())
cycles.Comparison_End = cycles.Comparison_End.apply(lambda x: datetime.datetime.strptime(x, '%m/%d/%Y').date())

if 'cycle_index' not in st.session_state:
    st.session_state['cycle_index'] = 0
    st.session_state['endDate'] = cycles.End[0];
    st.session_state['comparisonStartDate'] = cycles.Comparison_Start[0];
    st.session_state['comparisonEndDate'] = cycles.Comparison_End[0];

def setCycleDates():
    index = cycles.index[cycles['Start']==st.session_state['startDate']].tolist()[0]
    st.session_state['endDate'] = cycles.End[index];
    st.session_state['comparisonStartDate'] = cycles.Comparison_Start[index];
    st.session_state['comparisonEndDate'] = cycles.Comparison_End[index];

    st.session_state['cycle_index'] = index


with st.expander("Fechas", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        inicio = st.selectbox("Inicio", cycles['Start'], key="startDate", on_change=setCycleDates)
        #inicio = st.date_input("Inicio", datetime.date(2019, 7, 6))
    with col2:
        final = st.date_input("Final", key="endDate", disabled=True)

    col3, col4 = st.columns(2)
    with col3:
        inicioPrevio = st.date_input("Inicio (previo)", key="comparisonStartDate", disabled=True)
    with col4:    
        finalPrevio = st.date_input("Final (previo)", key="comparisonEndDate", disabled=True)

agents = pd.read_csv("data/agents.csv", encoding="latin1")
#agents.shape
agents = agents.loc[agents.Group == 'sales_group1']
#agents

sales = pd.read_csv("data/challenge_products.csv", sep='\t', encoding="latin1")
sales.paid_date = sales.paid_date.apply(lambda x: datetime.datetime.strptime(x.split(' ')[0], '%Y-%m-%d').date())
#sales.shape
#sales.head()
sales_g1 = sales.loc[sales.salesperson.isin(agents.Name)]
#sales_g1.shape

current_cycle_sales_g1 = sales_g1.loc[(sales.paid_date >= inicio) & (sales.paid_date <= final)]
#current_cycle_sales_g1.shape
previous_cycle_sales_g1 = sales_g1.loc[(sales.paid_date >= inicioPrevio) & (sales.paid_date <= finalPrevio)]
#previous_cycle_sales_g1.shape

cycle_goal = cycles.Goal[st.session_state['cycle_index']]
current_cycle_sales_sum =  current_cycle_sales_g1.price.sum()
previous_cycle_sales_sum = previous_cycle_sales_g1.price.sum()

compared_sales_vs_goal = (current_cycle_sales_sum)*100/cycle_goal
compared_sales = (current_cycle_sales_sum-previous_cycle_sales_sum)*100/previous_cycle_sales_sum

#cycle_goal
#current_cycle_sales_sum
#previous_cycle_sales_sum
#compared_sales_vs_goal
#compared_sales

meta_string = "Meta: "+str(cycle_goal)+" USD" 
st.header(meta_string)
progress = compared_sales_vs_goal if(compared_sales_vs_goal <= 100) else 100
my_bar = st.progress(progress, text=str(compared_sales_vs_goal)+'%')
current_sales_string = "Ahora: "+str(current_cycle_sales_sum)+" USD"
st.subheader(current_sales_string)
previous_sales_string = "Previo: "+str(previous_cycle_sales_sum)+" USD"
st.write(previous_sales_string)

sales_per_day_current_cycle = current_cycle_sales_g1.groupby('paid_date').sum()[['price']]
sales_per_day_previous_cycle = previous_cycle_sales_g1.groupby('paid_date').sum()[['price']]


sales_per_day_current_cycle.shape
sales_per_day_previous_cycle.shape

#sales_per_day_current_cycle
#sales_per_day_previous_cycle

#indexes = sales_per_day_current_cycle.index.values.flatten()
#indexes.shape

st.title("Uso de cupones")
current_cycle_sales_g1_grouped_by_coupons = current_cycle_sales_g1.groupby('coupon', as_index="False").agg(count=("coupon", "count"))
#current_cycle_sales_g1_grouped_by_coupons
previous_cycle_sales_g1_grouped_by_coupons = previous_cycle_sales_g1.groupby('coupon', as_index="False").agg(count=("coupon", "count"))
#previous_cycle_sales_g1_grouped_by_coupons

grouped_by_coupons = current_cycle_sales_g1_grouped_by_coupons.merge(previous_cycle_sales_g1_grouped_by_coupons, on="coupon", how="left")
grouped_by_coupons['Cupon'] = grouped_by_coupons.index

grouped_by_coupons['Variacion'] = ((grouped_by_coupons['count_x']-grouped_by_coupons['count_y'])*100/grouped_by_coupons['count_y']).astype(str).add('%')


total_coupons = grouped_by_coupons['count_x'].sum()
#total_coupons
grouped_by_coupons['Porcentaje'] = (grouped_by_coupons['count_x']*100/total_coupons).round(2).astype(str).add('%')
grouped_by_coupons['Usados'] = grouped_by_coupons['count_x']

grouped_by_coupons.loc[:, ['Cupon', 'Porcentaje', 'Usados', 'Variacion']]

st.subheader("Ventas")

#define figure and axes
fig, ax = plt.subplots()

#hide the axes
fig.patch.set_visible(False)
ax.axis('off')
ax.axis('tight')

#create data
df = pd.DataFrame(current_cycle_sales_g1, columns=['order_id', 'paid_date', 'price', 'sales_person', 'billing_country','coupon', 'order_item', 'course_category'])

#create table
table = ax.table(cellText=df.values, colLabels=['Order ID', 'Fecha', 'Precio (USD)', 'Asesor', 'País', 'Cupón', 'Item', 'Categoría'], loc='center')

#display table
fig.tight_layout()
plt.show()




#create values for table
table_data=[
    ["Player 1", 30],
    ["Player 2", 20],
    ["Player 3", 33],
    ["Player 4", 25],
    ["Player 5", 12]
]

#create table
table = ax.table(cellText=table_data, loc='center')

#modify table
table.set_fontsize(14)
table.scale(1,4)
ax.axis('off')

#display table
plt.show()
#create values for table
table_data=[
    ["Player 1", 30],
    ["Player 2", 20],
    ["Player 3", 33],
    ["Player 4", 25],
    ["Player 5", 12]
]

#create table
table = ax.table(cellText=table_data, loc='center')

#modify table
table.set_fontsize(14)
table.scale(1,4)
ax.axis('off')

#display table
plt.show()
