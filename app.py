import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import plotly.express as px

# Page config
st.set_page_config(page_title="Inventory Dashboard", layout="wide", page_icon="📦")

# Connect to SQLite
conn = sqlite3.connect("inventory.db", check_same_thread=False)
cursor = conn.cursor()

# Ensure table exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name TEXT NOT NULL,
    category TEXT,
    quantity INTEGER,
    reorder_level INTEGER,
    last_updated TEXT
)
""")
conn.commit()

# Load data
@st.cache_data
def load_data():
    return pd.read_sql_query("SELECT * FROM inventory", conn)

df = load_data()

# Sidebar navigation
st.sidebar.title("📁 Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "EDA", "Manage Inventory", "Chat with LLM"])

# ------------------ DASHBOARD ------------------
if page == "Dashboard":
    st.title("📦 Inventory Dashboard")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Products", df.shape[0])
    col2.metric("Total Stock", df["quantity"].sum())
    col3.metric("Low Stock Items", df[df["quantity"] < df["reorder_level"]].shape[0])

    st.subheader("📊 Stock Levels by Product")
    fig = px.bar(df, x="product_name", y="quantity", color="category", title="Stock by Product")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📋 Inventory Table")
    st.dataframe(df, use_container_width=True)

# ------------------ EDA ------------------
elif page == "EDA":
    st.title("📈 Exploratory Data Analysis")
    st.write("Visualize stock distribution and reorder risks.")

    st.subheader("🔍 Quantity Distribution")
    st.bar_chart(df.set_index("product_name")["quantity"])

    st.subheader("⚠️ Low Stock Products")
    low_stock = df[df["quantity"] < df["reorder_level"]]
    st.dataframe(low_stock)

# ------------------ MANAGE INVENTORY ------------------
elif page == "Manage Inventory":
    st.title("🛠️ Manage Inventory")

    st.subheader("➕ Add New Product")
    with st.form("add_product"):
        name = st.text_input("Product Name")
        category = st.text_input("Category")
        quantity = st.number_input("Quantity", min_value=0, step=1)
        reorder = st.number_input("Reorder Level", min_value=0, step=1)
        submitted = st.form_submit_button("Add Product")
        if submitted and name:
            cursor.execute("""
            INSERT INTO inventory (product_name, category, quantity, reorder_level, last_updated)
            VALUES (?, ?, ?, ?, ?)
            """, (name, category, quantity, reorder, datetime.now().strftime("%Y-%m-%d")))
            conn.commit()
            st.success(f"✅ Added {name} to inventory.")
            st.experimental_rerun()

    st.subheader("✏️ Edit Product Quantity")
    product = st.selectbox("Select Product to Edit", df["product_name"])
    new_qty = st.number_input("New Quantity", min_value=0, step=1)
    if st.button("Update Quantity"):
        cursor.execute("""
        UPDATE inventory SET quantity = ?, last_updated = ?
        WHERE product_name = ?
        """, (new_qty, datetime.now().strftime("%Y-%m-%d"), product))
        conn.commit()
        st.success(f"✅ Updated {product} to {new_qty} units.")
        st.experimental_rerun()

    st.subheader("🗑️ Delete Product")
    delete_product = st.selectbox("Select Product to Delete", df["product_name"], key="delete")
    if st.button("Delete Product"):
        cursor.execute("DELETE FROM inventory WHERE product_name = ?", (delete_product,))
        conn.commit()
        st.warning(f"⚠️ Deleted {delete_product} from inventory.")
        st.experimental_rerun()

# ------------------ CHAT WITH LLM ------------------
elif page == "Chat with LLM":
    st.title("💬 Ask About Your Inventory")

    st.markdown("Ask anything about your data. Examples:")
    st.markdown("- Which category has the lowest stock?")
    st.markdown("- What’s the average reorder level?")
    st.markdown("- Which products are below reorder threshold?")

    user_query = st.text_area("Your question", placeholder="e.g. Which products need restocking?")
    if st.button("Ask"):
        if user_query.strip():
            # Simulate LLM response using Pandas (replace with real LLM later)
            try:
                import io
                import contextlib
                local_vars = {"df": df}
                with contextlib.redirect_stdout(io.StringIO()) as f:
                    exec(f"print({user_query})", {}, local_vars)
                st.success("✅ Answer:")
                st.code(f.getvalue())
            except Exception as e:
                st.error(f"⚠️ Could not interpret query: {e}")
        else:
            st.warning("Please enter a question.")

# Close DB connection
conn.close()
