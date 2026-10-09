import os
from urllib.parse import quote_plus

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from sqlalchemy import create_engine, text
from dotenv import load_dotenv


st.set_page_config(
    page_title="Cart2Insights",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# DATABASE CONNECTION
# ---------------------------------------------------------

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# Check that database credentials are available
if not all([
    DB_HOST,
    DB_PORT,
    DB_USER,
    DB_PASSWORD,
    DB_NAME
]):
    st.error(
        "Database credentials are missing. "
        "Please check your .env file."
    )
    st.stop()

# Convert password into URL-safe format
password = quote_plus(DB_PASSWORD)

DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{password}@"
    f"{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

# Test database connection
try:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    st.sidebar.success("Database connected successfully.")

except Exception as e:
    st.error("Unable to connect to MySQL database.")
    st.exception(e)
    st.stop()


@st.cache_data(ttl=300)
def run_query(query, params=None):
    with engine.connect() as connection:
        return pd.read_sql(
            text(query),
            connection,
            params=params
        )


@st.cache_data(ttl=300)
def load_filter_data():

    categories = run_query("""
        SELECT DISTINCT
            COALESCE(
                ct.product_category_name_english,
                p.product_category_name,
                'Unknown'
            ) AS category_name
        FROM products p
        LEFT JOIN category_translation ct
            ON p.product_category_name =
               ct.product_category_name
        ORDER BY category_name
    """)

    statuses = run_query("""
        SELECT DISTINCT order_status
        FROM orders
        ORDER BY order_status
    """)

    dates = run_query("""
        SELECT
            MIN(order_purchase_timestamp) AS min_date,
            MAX(order_purchase_timestamp) AS max_date
        FROM orders
    """)

    return categories, statuses, dates


categories_df, statuses_df, dates_df = load_filter_data()

categories = categories_df["category_name"].dropna().tolist()

statuses = statuses_df["order_status"].dropna().tolist()

min_date = pd.to_datetime(
    dates_df["min_date"].iloc[0]
).date()

max_date = pd.to_datetime(
    dates_df["max_date"].iloc[0]
).date()


st.sidebar.title("🛒 Cart2Insights")

st.sidebar.markdown(
    "### E-Commerce Performance Dashboard"
)

st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Select Dashboard Section",
    [
        "Business Overview",
        "Sales Analysis",
        "Customer Analysis",
        "Seller & Product Analysis",
        "Delivery Analysis",
        "Customer Experience"
    ]
)


st.sidebar.markdown("---")
st.sidebar.subheader("Filters")


# order status filter 
selected_status = st.sidebar.multiselect(
    "Order Status",
    options=statuses,
    default=statuses
)


#category filter
selected_categories = st.sidebar.multiselect(
    "Product Category",
    options=categories,
    default=[]
)


#date filter
selected_date_range = st.sidebar.date_input(
    "Order Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)
if isinstance(selected_date_range, tuple):

    start_date = selected_date_range[0]
    end_date = selected_date_range[-1]

else:

    start_date = selected_date_range
    end_date = selected_date_range


#Page title
st.title("🛒 Cart2Insights")
st.caption(
    "Decoding E-Commerce Performance "
    "using Python, SQL, Statistics and Streamlit"
)


def build_order_filters():
    conditions = [
        "DATE(o.order_purchase_timestamp) BETWEEN :start_date AND :end_date"
    ]

    params = {
        "start_date": start_date,
        "end_date": end_date
    }

    # Order status filter
    if selected_status:
        status_placeholders = []

        for i, status in enumerate(selected_status):
            key = f"status_{i}"
            status_placeholders.append(f":{key}")
            params[key] = status

        conditions.append(
            "o.order_status IN ("
            + ", ".join(status_placeholders)
            + ")"
        )

    return " AND ".join(conditions), params
# ---------------------------------------------------------
# BUILD COMMON FILTERS
# ---------------------------------------------------------

filter_sql, params = build_order_filters()


# ---------------------------------------------------------
# DASHBOARD SECTIONS
# ---------------------------------------------------------


if page == "Business Overview":
    st.header("📊 Business Overview")

    st.write(
        "High-level view of overall e-commerce performance."
    )

    

    overview_query = f"""
        SELECT
            COUNT(DISTINCT o.order_id) AS total_orders,
            ROUND(
                COALESCE(SUM(oi.price + oi.freight_value), 0),
                2
            ) AS total_revenue,
            ROUND(
                COALESCE(
                    SUM(oi.price + oi.freight_value)
                    / NULLIF(COUNT(DISTINCT o.order_id), 0),
                    0
                ),
                2
            ) AS average_order_value,
            COUNT(DISTINCT o.customer_id) AS total_customers
        FROM orders o
        LEFT JOIN order_items oi
            ON o.order_id = oi.order_id
        WHERE {filter_sql}
    """

    overview = run_query(
        overview_query,
        params
    )


    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Orders",
        f"{int(overview['total_orders'].iloc[0]):,}"
    )

    col2.metric(
        "Total Revenue",
        f"₹{overview['total_revenue'].iloc[0]:,.2f}"
    )

    col3.metric(
        "Average Order Value",
        f"₹{overview['average_order_value'].iloc[0]:,.2f}"
    )

    col4.metric(
        "Total Customers",
        f"{int(overview['total_customers'].iloc[0]):,}"
    )


    review_query = """
        SELECT
            ROUND(AVG(review_score), 2) AS average_review_score
        FROM order_reviews
    """

    review_data = run_query(review_query)

    seller_query = """
        SELECT COUNT(*) AS total_sellers
        FROM sellers
    """

    seller_data = run_query(seller_query)

    col5, col6 = st.columns(2)

    col5.metric(
        "Total Sellers",
        f"{int(seller_data['total_sellers'].iloc[0]):,}"
    )

    col6.metric(
        "Average Review Score",
        f"{review_data['average_review_score'].iloc[0]:.2f} / 5"
    )


#monthly overview
    monthly_query = f"""
        SELECT
            DATE_FORMAT(
                o.order_purchase_timestamp,
                '%Y-%m'
            ) AS order_month,
            ROUND(
                SUM(oi.price + oi.freight_value),
                2
            ) AS revenue
        FROM orders o
        JOIN order_items oi
            ON o.order_id = oi.order_id
        WHERE {filter_sql}
        GROUP BY order_month
        ORDER BY order_month
    """

    monthly_data = run_query(
        monthly_query,
        params
    )


#chart
    fig = px.line(
        monthly_data,
        x="order_month",
        y="revenue",
        markers=True,
        title="Monthly Revenue Trend"
    )

    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Revenue"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


#order status
    status_query = f"""
        SELECT
            o.order_status,
            COUNT(DISTINCT o.order_id) AS orders
        FROM orders o
        WHERE {filter_sql}
        GROUP BY o.order_status
        ORDER BY orders DESC
    """

    status_data = run_query(
        status_query,
        params
    )


    fig = px.bar(
        status_data,
        x="order_status",
        y="orders",
        title="Orders by Status"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


#sales analysis
elif page == "Sales Analysis":
    st.header("💰 Sales Analysis")

    st.write(
        "Analyze revenue trends, categories, "
        "products and sales performance."
    )


#monthly sales

    sales_query = f"""
        SELECT
            DATE_FORMAT(
                o.order_purchase_timestamp,
                '%Y-%m'
            ) AS order_month,
            COUNT(DISTINCT o.order_id) AS orders,
            ROUND(
                SUM(oi.price + oi.freight_value),
                2
            ) AS revenue
        FROM orders o
        JOIN order_items oi
            ON o.order_id = oi.order_id
        WHERE {filter_sql}
        GROUP BY order_month
        ORDER BY order_month
    """

    sales_data = run_query(
        sales_query,
        params
    )


    col1, col2 = st.columns(2)

    with col1:

        fig = px.line(
            sales_data,
            x="order_month",
            y="orders",
            markers=True,
            title="Monthly Orders"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with col2:

        fig = px.line(
            sales_data,
            x="order_month",
            y="revenue",
            markers=True,
            title="Monthly Revenue"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


#sales revenue by category
    category_query = f"""
        SELECT
            COALESCE(
                ct.product_category_name_english,
                p.product_category_name,
                'Unknown'
            ) AS category_name,
            ROUND(
                SUM(oi.price + oi.freight_value),
                2
            ) AS revenue
        FROM orders o
        JOIN order_items oi
            ON o.order_id = oi.order_id
        JOIN products p
            ON oi.product_id = p.product_id
        LEFT JOIN category_translation ct
            ON p.product_category_name =
               ct.product_category_name
        WHERE {filter_sql}
        GROUP BY category_name
        ORDER BY revenue DESC
        LIMIT 15
    """

    category_data = run_query(
        category_query,
        params
    )


#chart
    fig = px.bar(
        category_data,
        x="revenue",
        y="category_name",
        orientation="h",
        title="Top 15 Categories by Revenue"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


#sales - top product
    product_query = f"""
        SELECT
            p.product_id,
            COALESCE(
                ct.product_category_name_english,
                p.product_category_name,
                'Unknown'
            ) AS category_name,
            ROUND(
                SUM(oi.price + oi.freight_value),
                2
            ) AS revenue,
            COUNT(*) AS items_sold
        FROM orders o
        JOIN order_items oi
            ON o.order_id = oi.order_id
        JOIN products p
            ON oi.product_id = p.product_id
        LEFT JOIN category_translation ct
            ON p.product_category_name =
               ct.product_category_name
        WHERE {filter_sql}
        GROUP BY
            p.product_id,
            category_name
        ORDER BY revenue DESC
        LIMIT 10
    """

    product_data = run_query(
        product_query,
        params
    )
    st.subheader("Top 10 Products")

    st.table(
        product_data
    )


#customer analysis 
elif page == "Customer Analysis":
    st.header("👥 Customer Analysis")

    st.write(
        "Analyze customer distribution, spending "
        "and repeat purchasing behavior."
    )

    customer_query = f"""
        SELECT
            COUNT(DISTINCT c.customer_unique_id)
                AS total_customers,

            COUNT(DISTINCT o.order_id)
                AS total_orders,

            ROUND(
                SUM(oi.price + oi.freight_value),
                2
            ) AS total_spending

        FROM orders o

        JOIN customers c
            ON o.customer_id = c.customer_id

        LEFT JOIN order_items oi
            ON o.order_id = oi.order_id

        WHERE {filter_sql}
    """

    customer_data = run_query(
        customer_query,
        params
    )


    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Customers",
        f"{int(customer_data['total_customers'].iloc[0]):,}"
    )

    col2.metric(
        "Orders",
        f"{int(customer_data['total_orders'].iloc[0]):,}"
    )

    col3.metric(
        "Customer Spending",
        f"₹{customer_data['total_spending'].iloc[0]:,.2f}"
    )


#repeat vs one time customer
    repeat_query = """
        SELECT
            CASE
                WHEN COUNT(DISTINCT o.order_id) > 1
                    THEN 'Repeat Customer'
                ELSE 'One-Time Customer'
            END AS customer_type,

            COUNT(*) AS customers

        FROM customers c

        JOIN orders o
            ON c.customer_id = o.customer_id

        GROUP BY c.customer_unique_id
    """

    repeat_data = run_query(
        repeat_query
    )

    repeat_summary = (
        repeat_data
        .groupby("customer_type")["customers"]
        .sum()
        .reset_index()
    )


    fig = px.pie(
        repeat_summary,
        names="customer_type",
        values="customers",
        title="Repeat vs One-Time Customers"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


#top customers
    top_customer_query = f"""
        SELECT
            c.customer_unique_id,
            COUNT(DISTINCT o.order_id)
                AS order_count,
            ROUND(
                SUM(oi.price + oi.freight_value),
                2
            ) AS total_spending

        FROM orders o

        JOIN customers c
            ON o.customer_id = c.customer_id

        JOIN order_items oi
            ON o.order_id = oi.order_id

        WHERE {filter_sql}

        GROUP BY c.customer_unique_id

        ORDER BY total_spending DESC

        LIMIT 10
    """

    top_customers = run_query(
        top_customer_query,
        params
    )

    st.subheader("Top 10 Customers by Spending")

    st.dataframe(
        top_customers,
        use_container_width=True
    )


#seller and product analysis
elif page == "Seller & Product Analysis":
    st.header("🏪 Seller & Product Analysis")

    st.write(
        "Analyze seller performance and "
        "product/category performance."
    )

    # Top sellers
    seller_query = f"""
        SELECT
            s.seller_id,
            s.seller_city,
            s.seller_state,

            COUNT(DISTINCT o.order_id)
                AS order_count,

            COUNT(oi.order_id)
                AS items_sold,

            ROUND(
                SUM(oi.price),
                2
            ) AS seller_revenue

        FROM sellers s

        JOIN order_items oi
            ON s.seller_id = oi.seller_id

        JOIN orders o
            ON oi.order_id = o.order_id

        WHERE {filter_sql}

        GROUP BY
            s.seller_id,
            s.seller_city,
            s.seller_state

        ORDER BY seller_revenue DESC

        LIMIT 15
    """

    seller_data = run_query(
        seller_query,
        params
    )


    fig = px.bar(
        seller_data,
        x="seller_revenue",
        y="seller_id",
        orientation="h",
        title="Top Sellers by Revenue"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


#seller performance table
    st.subheader("Seller Performance")

    st.dataframe(
        seller_data,
        use_container_width=True
    )


#product performance
    product_performance_query = f"""
        SELECT
            p.product_id,

            COALESCE(
                ct.product_category_name_english,
                p.product_category_name,
                'Unknown'
            ) AS category_name,

            COUNT(oi.order_id)
                AS items_sold,

            COUNT(DISTINCT o.order_id)
                AS order_count,

            ROUND(
                SUM(oi.price),
                2
            ) AS revenue

        FROM products p

        JOIN order_items oi
            ON p.product_id = oi.product_id

        JOIN orders o
            ON oi.order_id = o.order_id

        LEFT JOIN category_translation ct
            ON p.product_category_name =
               ct.product_category_name

        WHERE {filter_sql}

        GROUP BY
            p.product_id,
            category_name

        ORDER BY revenue DESC

        LIMIT 15
    """

    product_performance = run_query(
        product_performance_query,
        params
    )


    st.subheader("Top Products")

    st.dataframe(
        product_performance,
        use_container_width=True
    )


#delivery analysis
elif page == "Delivery Analysis":
    st.header("🚚 Delivery Analysis")

    st.write(
        "Analyze delivery time, delivery delays "
        "and on-time performance."
    )

    # Delivery KPIs
    delivery_query = f"""
        SELECT
            ROUND(
                AVG(
                    TIMESTAMPDIFF(
                        DAY,
                        o.order_purchase_timestamp,
                        o.order_delivered_customer_date
                    )
                ),
                2
            ) AS average_delivery_days,

            ROUND(
                AVG(
                    DATEDIFF(
                        o.order_delivered_customer_date,
                        o.order_estimated_delivery_date
                    )
                ),
                2
            ) AS average_delivery_delay,

            COUNT(
                CASE
                    WHEN o.order_delivered_customer_date IS NOT NULL
                    THEN 1
                END
            ) AS delivered_orders

        FROM orders o

        WHERE {filter_sql}
    """

    delivery_data = run_query(
        delivery_query,
        params
    )


    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Average Delivery Days",
        f"{delivery_data['average_delivery_days'].iloc[0]:.2f}"
    )

    col2.metric(
        "Average Delivery Delay",
        f"{delivery_data['average_delivery_delay'].iloc[0]:.2f} days"
    )

    col3.metric(
        "Delivered Orders",
        f"{int(delivery_data['delivered_orders'].iloc[0]):,}"
    )


#on-time vs delayed
    delivery_status_query = f"""
        SELECT

            CASE

                WHEN o.order_delivered_customer_date IS NULL
                    THEN 'Not Delivered'

                WHEN o.order_estimated_delivery_date IS NULL
                    THEN 'No Estimate'

                WHEN DATEDIFF(
                    o.order_delivered_customer_date,
                    o.order_estimated_delivery_date
                ) > 0
                    THEN 'Late'

                WHEN DATEDIFF(
                    o.order_delivered_customer_date,
                    o.order_estimated_delivery_date
                ) = 0
                    THEN 'On Time'

                ELSE 'Early'

            END AS delivery_status,

            COUNT(*) AS orders

        FROM orders o

        WHERE {filter_sql}

        GROUP BY delivery_status

        ORDER BY orders DESC
    """

    delivery_status_data = run_query(
        delivery_status_query,
        params
    )


    fig = px.bar(
        delivery_status_data,
        x="delivery_status",
        y="orders",
        title="Delivery Performance"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


#Delivery delay vs review score
    delivery_review_query = f"""
        SELECT

            CASE

                WHEN DATEDIFF(
                    o.order_delivered_customer_date,
                    o.order_estimated_delivery_date
                ) > 0
                    THEN 'Late'

                WHEN DATEDIFF(
                    o.order_delivered_customer_date,
                    o.order_estimated_delivery_date
                ) = 0
                    THEN 'On Time'

                WHEN DATEDIFF(
                    o.order_delivered_customer_date,
                    o.order_estimated_delivery_date
                ) < 0
                    THEN 'Early'

                ELSE 'Unknown'

            END AS delivery_status,

            ROUND(
                AVG(r.review_score),
                2
            ) AS average_review_score

        FROM orders o

        JOIN order_reviews r
            ON o.order_id = r.order_id

        WHERE {filter_sql}

        GROUP BY delivery_status
    """

    delivery_review_data = run_query(
        delivery_review_query,
        params
    )


    fig = px.bar(
        delivery_review_data,
        x="delivery_status",
        y="average_review_score",
        title="Review Score by Delivery Performance"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


#customer experience
elif page == "Customer Experience":
    st.header("⭐ Customer Experience")

    st.write(
        "Analyze review scores, customer satisfaction "
        "and delivery experience."
    )

    # ---------------------------------------------------------
    # REVIEW SCORE DISTRIBUTION
    # ---------------------------------------------------------

    review_query = """
        SELECT
            review_score,
            COUNT(*) AS review_count
        FROM order_reviews
        WHERE review_score IS NOT NULL
        GROUP BY review_score
        ORDER BY review_score
    """

    review_df = run_query(review_query)

    st.subheader("Review Score Distribution")

    if not review_df.empty:

        fig = px.bar(
            review_df,
            x="review_score",
            y="review_count",
            title="Review Score Distribution",
            labels={
                "review_score": "Review Score",
                "review_count": "Number of Reviews"
            }
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.dataframe(
            review_df,
            use_container_width=True
        )

    else:
        st.info("No review data available.")


    # ---------------------------------------------------------
    # AVERAGE REVIEW SCORE
    # ---------------------------------------------------------

    average_review_query = """
        SELECT
            ROUND(AVG(review_score), 2) AS average_review_score,
            COUNT(*) AS total_reviews
        FROM order_reviews
        WHERE review_score IS NOT NULL
    """

    average_review_df = run_query(
        average_review_query
    )

    st.subheader("Overall Customer Satisfaction")

    if not average_review_df.empty:

        col1, col2 = st.columns(2)

        col1.metric(
            "Average Review Score",
            f"{average_review_df['average_review_score'].iloc[0]:.2f} / 5"
        )

        col2.metric(
            "Total Reviews",
            f"{average_review_df['total_reviews'].iloc[0]:,}"
        )


    # ---------------------------------------------------------
    # DELIVERY PERFORMANCE VS REVIEW SCORE
    # ---------------------------------------------------------

    experience_query = """
        SELECT
            o.delivery_status,

            ROUND(
                AVG(r.review_score),
                2
            ) AS average_review_score,

            COUNT(*) AS reviewed_orders

        FROM order_features o

        JOIN order_reviews r
            ON o.order_id = r.order_id

        WHERE r.review_score IS NOT NULL

        GROUP BY
            o.delivery_status

        ORDER BY
            average_review_score DESC
    """

    experience_df = run_query(
        experience_query
    )

    st.subheader(
        "Customer Satisfaction by Delivery Performance"
    )

    if not experience_df.empty:

        st.table(
            experience_df
        )

        fig = px.bar(
            experience_df,
            x="delivery_status",
            y="average_review_score",
            title="Average Review Score by Delivery Status",
            labels={
                "delivery_status": "Delivery Status",
                "average_review_score": "Average Review Score"
            }
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:
        st.info(
            "No delivery experience data available."
        )


    # ---------------------------------------------------------
    # REVIEW SCORE BY DELIVERY STATUS
    # ---------------------------------------------------------

    review_delivery_query = """
        SELECT
            o.delivery_status,
            r.review_score,
            COUNT(*) AS review_count

        FROM order_features o

        JOIN order_reviews r
            ON o.order_id = r.order_id

        WHERE r.review_score IS NOT NULL

        GROUP BY
            o.delivery_status,
            r.review_score

        ORDER BY
            o.delivery_status,
            r.review_score
    """

    review_delivery_df = run_query(
        review_delivery_query
    )

    st.subheader(
        "Review Scores by Delivery Status"
    )

    if not review_delivery_df.empty:

        fig = px.bar(
            review_delivery_df,
            x="review_score",
            y="review_count",
            color="delivery_status",
            barmode="group",
            title="Review Score Distribution by Delivery Status",
            labels={
                "review_score": "Review Score",
                "review_count": "Number of Reviews",
                "delivery_status": "Delivery Status"
            }
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.dataframe(
            review_delivery_df,
            use_container_width=True
        )

    else:
        st.info(
            "No review and delivery data available."
        )


    # ---------------------------------------------------------
    # CATEGORY CUSTOMER EXPERIENCE
    # ---------------------------------------------------------

    category_experience_query = """
        SELECT
            COALESCE(
                ct.product_category_name_english,
                p.product_category_name,
                'Unknown'
            ) AS category_name,

            ROUND(
                AVG(r.review_score),
                2
            ) AS average_review_score,

            COUNT(*) AS reviewed_orders

        FROM order_reviews r

        JOIN order_items oi
            ON r.order_id = oi.order_id

        JOIN products p
            ON oi.product_id = p.product_id

        LEFT JOIN category_translation ct
            ON p.product_category_name =
               ct.product_category_name

        WHERE r.review_score IS NOT NULL

        GROUP BY
            COALESCE(
                ct.product_category_name_english,
                p.product_category_name,
                'Unknown'
            )

        HAVING COUNT(*) >= 20

        ORDER BY
            average_review_score DESC

        LIMIT 15
    """

    category_experience_df = run_query(
        category_experience_query
    )

    st.subheader(
        "Customer Satisfaction by Product Category"
    )

    if not category_experience_df.empty:

        fig = px.bar(
            category_experience_df.sort_values(
                "average_review_score"
            ),
            x="average_review_score",
            y="category_name",
            orientation="h",
            title="Average Review Score by Product Category",
            labels={
                "average_review_score": "Average Review Score",
                "category_name": "Product Category"
            }
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.dataframe(
            category_experience_df,
            use_container_width=True
        )

    else:
        st.info(
            "No category review data available."
        )


#footer
st.sidebar.markdown("---")

st.sidebar.caption(
    "Cart2Insights | E-Commerce Analytics"
)

st.sidebar.caption(
    "Built using Python, MySQL, Pandas and Streamlit"
)