# Cart2Insights: Decoding E-Commerce Performance

## Project Overview

Cart2Insights is an end-to-end e-commerce data analytics project designed to analyze sales performance, customer behavior, seller performance, product performance, delivery operations, and customer satisfaction.

The project uses a multi-table e-commerce dataset and follows a complete data analytics workflow:

- Data understanding
- Data cleaning
- Data quality validation
- SQL database design
- Feature engineering
- Exploratory Data Analysis (EDA)
- Statistical analysis
- SQL business analysis
- Interactive Streamlit dashboard
- Business insights and recommendations

The final objective is to transform raw e-commerce data into meaningful business insights that can support data-driven decision-making.

---

## Business Objectives

The major objectives of this project are:

1. Analyze overall e-commerce sales performance.
2. Identify revenue trends over time.
3. Identify high-performing product categories and products.
4. Analyze customer purchasing behavior.
5. Identify repeat and one-time customers.
6. Analyze seller performance and revenue.
7. Analyze delivery performance and delays.
8. Understand the relationship between delivery performance and customer satisfaction.
9. Analyze review scores and customer experience.
10. Present the results through an interactive business dashboard.

---

## Dataset

The project uses an e-commerce dataset containing multiple related tables.

The main tables used in the project are:

1. Sellers
2. Product Category Translation
3. Products
4. Customers
5. Geolocation
6. Orders
7. Order Items
8. Order Payments
9. Order Reviews

These tables are connected using primary and foreign-key relationships and are stored in a MySQL database for SQL-based analysis.

---

## Project Structure

```text
Cart2Insights/
│
├── app.py
├── README.md
├── requirements.txt
├── .gitignore
├── .env
│
├── data/
│   ├── raw/
│   └── cleaned/
│
└── notebooks/
    ├── Data Cleaning Notebooks
    ├── 10_sql_database_setup.ipynb
    ├── 11_feature_engineering.ipynb
    ├── 12_eda.ipynb
    ├── 13_statistical_analysis.ipynb
    └── 14_sql_analysis.ipynb

Technology Stack
Programming Language
- Python
Data Analysis
- Pandas
- NumPy
Database
- MySQL
Database Connectivity
- SQLAlchemy
- PyMySQL
- python-dotenv
Visualization
- Plotly
- Streamlit
Statistical Analysis
- SciPy
- Statsmodels
Development Environment
- Jupyter Notebook
- VS Code

Project Workflow
The project follows the following analytical workflow:
Raw Data
   ↓
Data Understanding
   ↓
Data Cleaning
   ↓
Data Quality Validation
   ↓
MySQL Database
   ↓
Feature Engineering
   ↓
Exploratory Data Analysis
   ↓
Statistical Analysis
   ↓
SQL Business Analysis
   ↓
Streamlit Dashboard
   ↓
Business Insights & Recommendations

1. Data Understanding
The first stage of the project involved understanding the structure and relationships between the different datasets.
The data was examined for:
- Number of rows and columns
- Column names
- Data types
- Primary keys
- Foreign keys
- Relationships between tables
- Missing values
- Duplicate records
- Categorical variables
- Numerical variables
- Date and timestamp fields
An understanding of the database relationships was established before beginning the cleaning and SQL stages.

2. Data Cleaning
Each dataset was cleaned individually using Pandas.
The cleaning process included:
- Checking dataset dimensions
- Checking column names
- Checking data types
- Detecting missing values
- Detecting duplicate records
- Validating primary keys
- Standardizing text fields
- Converting date and timestamp columns
- Checking invalid numerical values
- Checking negative values
- Checking outliers
- Preserving legitimate missing values where appropriate
The cleaned datasets were stored in:
data/cleaned/

3. SQL Database
The cleaned datasets were loaded into a MySQL database named:
cart2insights

The database contains the following tables:
- sellers
- category_translation
- products
- customers
- geolocation
- orders
- order_items
- order_payments
- order_reviews
Primary-key and foreign-key relationships were created to maintain referential integrity.
4. Feature Engineering
Feature engineering was performed using SQL views in MySQL.
The following feature views were created:
- order_features
- customer_features
- seller_features
- product_features
- category_features
- order_enriched_features
Order Features
The order-level features include:
- Item price total
- Freight total
- Order total value
- Delivery days
- Delivery delay days
- Delivery status
- Delayed-order indicator
Order Total Value
Order total value is calculated as:
Order Total Value = Item Price Total + Freight Total

Delivery Days
Delivery days measure the time between:
Order Purchase Date → Customer Delivery Date

Delivery Delay
Delivery delay compares the actual delivery date with the estimated delivery date.
The delivery status is classified as:
- Early
- On Time
- Late
- Not Delivered
- Delivered - No Estimate

5. Customer Features
Customer-level features include:
- Customer order count
- Customer total spending
- Average order value
- Repeat customer indicator
- First order date
- Last order date
A customer is classified as a repeat customer when the customer has placed more than one order.

6. Seller Features
Seller-level features include:
- Seller revenue
- Seller order count
- Items sold
- Seller freight value
- Average item price
Seller revenue is based on product price and does not include freight.

7. Product Features
Product-level features include:
- Product category
- Category in English
- Items sold
- Order count
- Product revenue
- Product freight value

8. Category Features
Category-level features include:
- Product count
- Items sold
- Order count
- Category revenue
- Category freight value

9. Exploratory Data Analysis
Exploratory Data Analysis was performed to understand patterns and relationships in the data.
The analysis included:
# Univariate Analysis
Analysis of individual variables such as:
- Order status
- Review scores
- Product categories
- Revenue
- Delivery time

#Bivariate Analysis
Relationships between variables were analyzed, such as:
- Revenue by category
- Delivery performance vs review score
- Customer spending
- Seller revenue
Multivariate Analysis
Multiple variables were analyzed together to understand broader business patterns.
Time-Based Analysis
Monthly sales and revenue trends were analyzed using order purchase timestamps.

10. Statistical Analysis
Statistical tests were performed to support business conclusions.
The following tests were used:
Independent Two-Sample T-Test
Used to compare review scores between delayed and on-time orders.
Hypotheses

Null Hypothesis (H0):
There is no significant difference in average review scores between delayed and on-time orders.
Alternative Hypothesis (H1):
There is a significant difference in average review scores between delayed and on-time orders.
One-Way ANOVA
Used to analyze whether average order value differs across product categories.
Hypotheses

Null Hypothesis (H0):
There is no significant difference in average order value among product categories.
Alternative Hypothesis (H1):
At least one product category has a significantly different average order value.
Chi-Square Test
Used to analyze the relationship between payment method and order status.
Hypotheses

Null Hypothesis (H0):
Payment method and order status are independent.
Alternative Hypothesis (H1):
Payment method and order status are associated.
The statistical tests were evaluated using p-values and appropriate decision rules.

11. SQL Business Analysis
SQL analysis was performed using the MySQL database.
The SQL analysis notebook demonstrates:
- SELECT
- WHERE
- ORDER BY
- GROUP BY
- HAVING
- JOINs
- Aggregations
- Subqueries
- Common Table Expressions (CTEs)
- Window Functions
Business-oriented SQL analyses include:
- Order status analysis
- Seller revenue analysis
- Monthly revenue trends
- Delivery performance
- Product category performance
- Customer spending
- Seller ranking

12. Streamlit Dashboard
An interactive Streamlit dashboard was developed to present the analytical results.
The dashboard contains six major sections.
Business Overview
This section provides high-level business KPIs including:
- Total Revenue
- Total Orders
- Total Customers
- Total Sellers
- Average Order Value
- Average Review Score
Sales Analysis
This section analyzes:
- Monthly revenue trends
- Revenue by product category
- Top-performing products
- Sales by location
Customer Analysis
This section analyzes:
- Customer distribution
- Customer spending
- Average order value
- Repeat vs one-time customers
- Top customers
Seller & Product Analysis
This section analyzes:
- Top sellers
- Seller revenue
- Seller order volume
- Product performance
- Product category performance
- Seller ratings
Delivery Analysis
This section analyzes:
- Average delivery time
- Delivery status
- On-time vs delayed orders
- Delivery performance by location
- Delivery delay and customer review scores
Customer Experience
This section analyzes:
- Review score distribution
- Average customer review score
- Customer satisfaction by delivery status
- Review scores by delivery status
- Customer satisfaction by product category

13. Dashboard Filters
The Streamlit dashboard provides interactive filters including:
- Order Status
- Product Category
- Date Range
These filters allow users to explore the business data dynamically.

14. Running the Project
Step 1: Install Dependencies
Install the required Python packages:
pip install -r requirements.txt

Step 2: Configure Database Credentials
Create a .env file in the project root.
Example:
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=cart2insights

Do not share or upload the .env file.
Step 3: Create the Database
Create the MySQL database:
CREATE DATABASE cart2insights;

Then execute the database setup notebook:
10_sql_database_setup.ipynb

This creates the required tables and loads the cleaned datasets.
Step 4: Create Feature Views
Run:
11_feature_engineering.ipynb

This creates the SQL feature views required by the analysis and dashboard.
Step 5: Run EDA and Statistical Analysis
Run:
12_eda.ipynb
13_statistical_analysis.ipynb
14_sql_analysis.ipynb

These notebooks contain the exploratory, statistical, and SQL business analyses.
Step 6: Launch the Dashboard
Run the following command from the project root:
streamlit run app.py

The Streamlit dashboard will open in the browser.
15. Key Business Questions
The project addresses questions such as:
1. How is revenue changing over time?
2. Which product categories generate the highest revenue?
3. Which products are the top performers?
4. Which customers contribute the most revenue?
5. What proportion of customers are repeat customers?
6. Which sellers generate the most revenue?
7. How long does delivery typically take?
8. How frequently are orders delayed?
9. Does delivery performance affect customer satisfaction?
10. Which product categories receive higher customer ratings?
11. Which locations have stronger sales performance?
12. Which sellers have stronger customer ratings?
16. Business Insights and Recommendations
The final stage of the project converts analytical findings into actionable business recommendations.

Insights should follow the structure:
Observation
     ↓
Interpretation
     ↓
Business Impact
     ↓
Recommendation

Examples of areas for recommendations include:

Sales
Identify high-performing categories and products and focus inventory and marketing efforts on products with strong demand.

Customer Retention
Use repeat-customer analysis to understand customer loyalty and identify opportunities for targeted retention campaigns.

Seller Performance
Identify high-performing sellers and investigate sellers with low revenue or low customer ratings.

Delivery
Identify locations or orders with higher delivery delays and investigate logistics or fulfillment bottlenecks.

Customer Experience
Analyze low review scores and determine whether delivery performance, product categories, or seller performance contribute to lower customer satisfaction.

17. Security and Data Handling
Database credentials are stored in a .env file.
The .env file should not be committed to GitHub.
The .gitignore file excludes sensitive configuration files and Python-generated files.
Example:
.env
__pycache__/
.ipynb_checkpoints/
*.pyc
.venv/
venv/

18. Project Deliverables
The completed project contains:
- Cleaned datasets
- Data cleaning notebooks
- MySQL database
- SQL schema and relationships
- Feature engineering SQL views
- Exploratory Data Analysis
- Statistical analysis
- SQL business analysis
- Streamlit dashboard
- Requirements file
- README documentation
- Business insights and recommendations

19. Conclusion
Cart2Insights provides an end-to-end analytical workflow for understanding e-commerce performance.
The project combines Python-based data preparation, MySQL database management, SQL analytics, statistical analysis, feature engineering, and interactive visualization to transform raw e-commerce data into actionable business insights.
The final Streamlit dashboard allows users to interactively explore sales, customers, sellers, products, delivery performance, and customer experience.
