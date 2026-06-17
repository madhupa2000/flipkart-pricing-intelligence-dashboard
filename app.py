import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(
    page_title="Flipkart Pricing Intelligence Dashboard",
    layout="wide"
)

st.title("📊 Flipkart Pricing Intelligence Dashboard")

st.markdown("""
Analyze pricing strategies, discount patterns, category performance,
and brand positioning across Flipkart products.
""")

# ----------------------------
# DATA LOADING
# ----------------------------

@st.cache_data
def load_data():

    df = pd.read_csv("data/flipkart_com-ecommerce_sample.csv")

    df = df.drop_duplicates()

    df = df.dropna(
        subset=[
            "retail_price",
            "discounted_price"
        ]
    )

    df["retail_price"] = pd.to_numeric(
        df["retail_price"],
        errors="coerce"
    )

    df["discounted_price"] = pd.to_numeric(
        df["discounted_price"],
        errors="coerce"
    )

    df = df[
        (df["retail_price"] > 0)
        &
        (df["discounted_price"] > 0)
    ]

    df["category"] = (
        df["product_category_tree"]
        .str.split(">>")
        .str[0]
        .str.replace('[","[]', '', regex=True)
        .str.strip()
    )

    df["discount_percent"] = (
        (
            df["retail_price"]
            - df["discounted_price"]
        )
        /
        df["retail_price"]
    ) * 100

    return df


df = load_data()

# ----------------------------
# KPI SECTION
# ----------------------------

total_products = len(df)

total_categories = df["category"].nunique()

total_brands = df["brand"].nunique()

avg_discount = round(
    df["discount_percent"].mean(),
    2
)

avg_price = round(
    df["discounted_price"].mean(),
    2
)

# ----------------------------
# TABS
# ----------------------------

tab1, tab2, tab3 = st.tabs([
    "📈 Executive Summary",
    "📦 Category Analysis",
    "🏷️ Brand Analysis"
])

# =====================================================
# TAB 1
# =====================================================

with tab1:

    st.subheader("Marketplace Overview")

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric("Products", f"{total_products:,}")
    c2.metric("Categories", total_categories)
    c3.metric("Brands", total_brands)
    c4.metric("Avg Price", f"₹{avg_price:,.0f}")
    c5.metric("Avg Discount", f"{avg_discount}%")

    st.divider()

    st.subheader("Top Categories Overview")

    category_summary = (
        df.groupby("category")
        .agg(
            Products=("category", "count"),
            Avg_Price=("discounted_price", "mean"),
            Avg_Discount=("discount_percent", "mean")
        )
        .sort_values(
            "Products",
            ascending=False
        )
        .head(10)
    )

    st.dataframe(
        category_summary.round(2),
        use_container_width=True
    )

    st.subheader("Discount Distribution")

    fig, ax = plt.subplots(figsize=(8, 3))

    sns.histplot(
        df["discount_percent"],
        bins=25,
        kde=True,
        ax=ax
    )

    ax.set_xlabel("Discount %")

    st.pyplot(fig)

# =====================================================
# TAB 2
# =====================================================

with tab2:

    st.subheader("Category Performance Analysis")

    category_analysis = (
        df.groupby("category")
        .agg(
            Products=("category", "count"),
            Avg_Price=("discounted_price", "mean"),
            Avg_Discount=("discount_percent", "mean")
        )
    )

    category_analysis["Revenue_Potential"] = (
        category_analysis["Products"]
        * category_analysis["Avg_Price"]
    )

    category_analysis = (
        category_analysis
        .sort_values(
            "Revenue_Potential",
            ascending=False
        )
    )

    st.dataframe(
        category_analysis.round(2),
        use_container_width=True
    )

    st.subheader(
        "Top 10 Categories by Revenue Potential"
    )

    top10 = category_analysis.head(10)

    fig, ax = plt.subplots(figsize=(8, 4))

    sns.barplot(
        x=top10["Revenue_Potential"],
        y=top10.index,
        ax=ax
    )

    ax.set_xlabel("Revenue Potential")

    st.pyplot(fig)

# =====================================================
# TAB 3
# =====================================================

with tab3:

    st.subheader("Brand Performance Analysis")

    brand_analysis = (
        df.groupby("brand")
        .agg(
            Products=("brand", "count"),
            Avg_Price=("discounted_price", "mean"),
            Avg_Discount=("discount_percent", "mean")
        )
        .sort_values(
            "Products",
            ascending=False
        )
    )

    st.dataframe(
        brand_analysis.head(20).round(2),
        use_container_width=True
    )

    st.subheader(
        "Top 10 Brands by Product Count"
    )

    fig, ax = plt.subplots(figsize=(8, 4))

    sns.barplot(
        x=brand_analysis.head(10)["Products"],
        y=brand_analysis.head(10).index,
        ax=ax
    )

    ax.set_xlabel("Number of Products")

    st.pyplot(fig)

    st.subheader(
        "Premium Brands (Highest Avg Price)"
    )

    premium_brands = (
        brand_analysis
        .sort_values(
            "Avg_Price",
            ascending=False
        )
        .head(10)
    )

    fig, ax = plt.subplots(figsize=(8, 4))

    sns.barplot(
        x=premium_brands["Avg_Price"],
        y=premium_brands.index,
        ax=ax
    )

    ax.set_xlabel("Average Price")

    st.pyplot(fig)

# =====================================================
# BUSINESS INSIGHTS
# =====================================================

st.divider()

highest_discount_category = (
    df.groupby("category")["discount_percent"]
    .mean()
    .idxmax()
)

highest_price_category = (
    df.groupby("category")["discounted_price"]
    .mean()
    .idxmax()
)

st.subheader("📌 Key Business Insights")

st.success(
    f"Highest average discount category: {highest_discount_category}"
)

st.info(
    f"Highest average selling price category: {highest_price_category}"
)

st.markdown("""
### Recommendations

- Focus marketing efforts on categories with high discount responsiveness.
- Premium categories offer significant revenue opportunities.
- Monitor dominant brands for competitive pricing strategies.
- Use category-specific pricing tactics rather than blanket discounts.
- Track high-value categories for inventory and promotion planning.
""")