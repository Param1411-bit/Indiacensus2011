import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------- PAGE CONFIG ---------------- #
st.set_page_config(
    page_title="India Census Dashboard",
    page_icon="🇮🇳",
    layout="wide"
)

# ---------------- LOAD DATA ---------------- #
@st.cache_data
def load_data():
    df = pd.read_csv('india.csv')
    # Remove duplicate columns
    df = df.loc[:, ~df.columns.duplicated()]
    # Strip spaces (IMPORTANT)
    df.columns = df.columns.str.strip()

    return df
df = load_data()

# ---------------- SIDEBAR ---------------- #
st.sidebar.title('📊 India Census 2011 Dashboard')

states = list(df['State'].unique())
states.insert(0, 'Overall India')

selected_state = st.sidebar.selectbox('Select State', states)

numeric_cols = df.select_dtypes(include='number').columns.tolist()
# Remove problematic columns
numeric_cols = [col for col in numeric_cols if col not in ['Latitude', 'Longitude']]

primary = st.sidebar.selectbox('Primary Parameter', numeric_cols)
secondary = st.sidebar.selectbox('Secondary Parameter', numeric_cols)

# ---------------- TITLE ---------------- #
st.title('🇮🇳 India Census Interactive Dashboard')
st.markdown("Explore district-level insights across India using interactive visualizations.")

# ---------------- FILTER DATA ---------------- #
if selected_state == 'Overall India':
    data = df.copy()
else:
    data = df[df['State'] == selected_state]

# ---------------- KPI SECTION ---------------- #
st.subheader("📌 Key Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Districts", data.shape[0])

with col2:
    st.metric(f"Avg {primary}", round(data[primary].mean(), 2))

with col3:
    st.metric(f"Max {primary}", round(data[primary].max(), 2))

with col4:
    st.metric(f"Min {primary}", round(data[primary].min(), 2))

# ---------------- MAP ---------------- #
st.subheader("🗺️ Geographic Visualization")

fig_map = px.scatter_mapbox(
    data,
    lat="Latitude",
    lon="Longitude",
    size=primary,
    color=secondary,
    hover_name="District",
    zoom=4 if selected_state == 'Overall India' else 6,
    mapbox_style="carto-positron",
    height=600
)

st.plotly_chart(fig_map, use_container_width=True)

# ---------------- TOP 10 ---------------- #
st.subheader("🏆 Top 10 Districts")

top10 = data.sort_values(by=primary, ascending=False).head(10)

fig_bar = px.bar(
    top10,
    x='District',
    y=primary,
    color=secondary,
    text_auto=True
)

st.plotly_chart(fig_bar, use_container_width=True)

# ---------------- BOTTOM 10 ---------------- #
st.subheader("📉 Bottom 10 Districts")

bottom10 = data.sort_values(by=primary, ascending=True).head(10)

fig_bar2 = px.bar(
    bottom10,
    x='District',
    y=primary,
    color=secondary,
    text_auto=True
)

st.plotly_chart(fig_bar2, use_container_width=True)

# ---------------- DISTRIBUTION ---------------- #
st.subheader("📊 Distribution Analysis")

fig_hist = px.histogram(
    data,
    x=primary,
    nbins=30,
    marginal="box"
)

st.plotly_chart(fig_hist, use_container_width=True)

# ---------------- SCATTER ---------------- #
st.subheader("🔗 Relationship Analysis")

# Drop NaNs before plotting
scatter_data = data[[primary, secondary, "District"]].dropna()

fig_scatter = px.scatter(
    scatter_data,
    x=primary,
    y=secondary,
    hover_name="District",
    trendline="ols"
)

st.plotly_chart(fig_scatter, use_container_width=True)


# ---------------- HEATMAP ---------------- #
st.subheader("🔥 Correlation Heatmap")

corr = data[numeric_cols].corr()

fig_heatmap = px.imshow(
    corr,
    text_auto=True,
    aspect="auto"
)

st.plotly_chart(fig_heatmap, use_container_width=True)

# ---------------- INSIGHTS ---------------- #
st.subheader("🧠 Key Insights")

top_district = top10.iloc[0]['District']
bottom_district = bottom10.iloc[0]['District']

st.write(f"""
- 🔝 Highest {primary}: **{top_district}**
- 🔻 Lowest {primary}: **{bottom_district}**
- 📊 Average {primary}: **{round(data[primary].mean(),2)}**
- 🔗 There is a visible relationship between **{primary}** and **{secondary}**
""")

# ---------------- RAW DATA ---------------- #
st.subheader("📄 Dataset")

if st.checkbox("Show Raw Data"):
    st.dataframe(data)

# ---------------- DOWNLOAD ---------------- #
st.subheader("⬇️ Download Data")

csv = data.to_csv(index=False).encode('utf-8')

st.download_button(
    label="Download Filtered Data",
    data=csv,
    file_name='filtered_data.csv',
    mime='text/csv',
)