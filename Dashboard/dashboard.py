import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import seaborn as sns
import streamlit as st
import urllib
from babel.numbers import format_currency
sns.set(style='dark')
st.set_option('deprecation.showPyplotGlobalUse', False)

# Dataset
datetime_cols = ["order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date", "order_purchase_timestamp", "shipping_limit_date"]
all_data = pd.read_csv('./all_data.csv')
all_data.sort_values(by="order_approved_at", inplace=True)
all_data.reset_index(inplace=True)

# Geolocation Dataset
geo = pd.read_csv('./geolocation.csv')
data = geo.drop_duplicates(subset='customer_unique_id')


for col in datetime_cols:
    all_data[col] = pd.to_datetime(all_data[col])

min_date = all_data["order_approved_at"].min()
max_date = all_data["order_approved_at"].max()

# Sidebar
with st.sidebar:
    # Title
    st.title("Dashboard")

    # Logo Image
    st.image('https://cdn-icons-png.flaticon.com/128/2038/2038854.png', width=140)

st.header("E-Commerce Dashboard :package:")

##Order items
st.subheader("Order Items")
col1, col2 = st.columns(2)

sum_orders_items = all_data.groupby("product_category_name_english")["product_id"].count().reset_index()
sum_orders_items = sum_orders_items.rename(columns={"product_id": "products"})
sum_orders_items = sum_orders_items.sort_values(by="products", ascending=False)

with col1:
    total_items = sum_orders_items["products"].sum()
    st.markdown(f"Total Items: **{total_items}**")

with col2:
    avg_items = round(sum_orders_items["products"].mean())
    st.markdown(f"Average Items: **{avg_items}**")

fig, ax = plt.subplots(1, 2, figsize=(24, 6))

colors = ["#FF5722", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]  # Ganti warna grafik sesuai kebutuhan

# Produk terbanyak terjual
sns.barplot(x="products", y="product_category_name_english",
            data=sum_orders_items.sort_values(by="products", ascending=False).head(5),
            palette=colors, ax=ax[0])

ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("Top Selling Products", loc="center", fontsize=18)
ax[0].tick_params(axis='y', labelsize=15)

# Produk tersedikit terjual
sns.barplot(x="products", y="product_category_name_english",
            data=sum_orders_items.sort_values(by="products", ascending=True).head(5),
            palette=colors, ax=ax[1])

ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Low Selling Products", loc="center", fontsize=18)
ax[1].tick_params(axis='y', labelsize=15)

plt.suptitle("Sold Products", fontsize=20)

st.pyplot(fig)

##Total money spent by customers
st.subheader('Total Money Spent by Customers')
# convert to date time format
all_data['order_approved_at'] = pd.to_datetime(all_data['order_approved_at'])

  # Resample the data
monthly_spend_df = all_data.resample(rule='M', on='order_approved_at').agg({
    "payment_value": "sum"
})

monthly_spend_df.index = monthly_spend_df.index.strftime('%B') #mengubah format order_approved_at menjadi Tahun-Bulan
monthly_spend_df = monthly_spend_df.reset_index()
monthly_spend_df.rename(columns={
    "payment_value":"total_spend"
}, inplace=True)

monthly_spend_df = monthly_spend_df.sort_values('total_spend').drop_duplicates('order_approved_at', keep='last')
monthly_spend_df = monthly_spend_df.groupby(by="order_approved_at").mean().reset_index()
monthly_spend_df['order_approved_at'] = pd.Categorical(monthly_spend_df['order_approved_at'],
                                                        categories=['January', 'February', 'March', 'April', 'May', 'June',
                                                                    'July', 'August', 'September', 'October', 'November', 'December'],
                                                        ordered=True)

monthly_spend_df = monthly_spend_df.sort_values(by='order_approved_at')

fig, ax = plt.subplots(figsize=(10, 5))
plt.plot(
    monthly_spend_df["order_approved_at"],
    monthly_spend_df["total_spend"],
    marker='o',
    linewidth=2,
    color="#FF5722"
)
plt.title("Total money spent (average per year)", loc="center", fontsize=20)
plt.xticks(fontsize=10, rotation=25)
plt.yticks(fontsize=10)

for x,y in zip(monthly_spend_df["order_approved_at"], monthly_spend_df["total_spend"]):

    y_formatted = round(y / 1000000, 2)
    label = "{:.2f}".format(y_formatted)

    plt.annotate(label , # this is the value which we want to label (text)
                 (x,y), # x and y is the points location where we have to label
                 textcoords="offset points",
                 xytext=(0,6), # this for the distance between the points
                 # and the text label
                 ha='center')
    
ax.text(0.02, 0.95, "Values in millions", transform=ax.transAxes, fontsize=10, verticalalignment='top', bbox=dict(facecolor='white', alpha=0.5))


st.pyplot(fig)

##Rating score
st.subheader('Rating Score')
col1,col2 = st.columns(2)

review_scores = all_data['review_score'].value_counts().sort_values(ascending=False)

most_common_score = review_scores.idxmax()

sns.set(style="darkgrid")
val = review_scores.values

with col1:
    avg_review_score = round(sum(val*[5,4,1,3,2])/sum(val), 2)
    st.markdown(f"Average Review Score: **{avg_review_score}**")

with col2:
    st.markdown(f"Most Common Review Score: **{most_common_score}**")

fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(x=review_scores.index,
            y=review_scores.values,
            order=review_scores.index,
            palette=["#FF5722" if score == most_common_score else "#D3D3D3" for score in review_scores.index]
            )

plt.title("Total rating by customer", fontsize=15)
plt.xlabel("Rating")
plt.ylabel("Count")
plt.xticks(fontsize=12)

def addlabels(x,y):
    for i in range(len(x)):
        plt.text(i,y[i],y[i], ha= 'center')

addlabels(review_scores.index, review_scores.values)

st.pyplot(fig)

##Customer demographic
st.subheader("Customer Geolocation")

class BrazilMapPlotter:
    def __init__(self, data, plt, mpimg, urllib, st):
        self.data = data
        self.plt = plt
        self.mpimg = mpimg
        self.urllib = urllib
        self.st = st

    def plot(self):
        brazil = self.mpimg.imread(self.urllib.request.urlopen('https://i.pinimg.com/originals/3a/0c/e1/3a0ce18b3c842748c255bc0aa445ad41.jpg'),'jpg')
        ax = self.data.plot(kind="scatter", x="geolocation_lng", y="geolocation_lat", figsize=(10,10), alpha=0.3,s=0.3,c='maroon')
        self.plt.axis('off')
        self.plt.imshow(brazil, extent=[-73.98283055, -33.8,-33.75116944,5.4])
        self.st.pyplot()

map_plot = BrazilMapPlotter(data, plt, mpimg, urllib, st)
map_plot.plot()

with st.expander("Explanation"):
        st.write('Sesuai dengan grafik yang diperoleh bahwa banyak customer yang berasal negara Brazil (SP) bagian tenggara dan selatan yang merupakan kota-kota besar seperti wilayah Sao Paulo, Rio de Janeiro, Belo Horizonte, dan yang lainnya.')


st.caption('Daniswara Aditya P. 2024')