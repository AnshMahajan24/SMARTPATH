import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

from backend.path_logic import construct_graph, find_best_route
from backend.graph_builder import auto_generate_routes

# =================== PAGE CONFIGURATION ===================
st.set_page_config(page_title="📦 SmartPathPlanner", layout="wide")

# =================== CUSTOM STYLING ===================
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
        padding: 1rem;
    }
    h1, h2, h3 {
        color: #333;
    }
    .stButton>button {
        background-color: #007BFF;
        color: white;
        border-radius: 6px;
        padding: 0.6em 1em;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #0056b3;
    }
    .block-container {
        padding-top: 2rem;
    }
    .st-radio label {
        font-weight: bold;
    }
    .dataframe th {
        background-color: #f0f2f6;
    }
    </style>
""", unsafe_allow_html=True)

# =================== PAGE TITLE ===================
st.markdown("# SmartPathPlanner")
st.markdown("#### 🚚 Plan optimized routes using real-world distances and TSP logic.")
st.markdown("---")

# =================== INPUT MODE ===================
st.markdown("### 📥 Choose How You Want to Input Addresses")
input_mode = st.radio("", ["Manual Entry", "Upload CSV"], horizontal=True)

# Storage
locations = []
routes = []

# =================== MANUAL ENTRY ===================
if input_mode == "Manual Entry":
    st.markdown("### 📝 Enter Delivery Locations (Minimum 2)")
    num_locations = st.number_input("🔢 How many addresses?", min_value=2, max_value=20, step=1)

    for i in range(num_locations):
        address = st.text_input(f"📍 Address {i + 1}", key=f"addr_{i}")
        if address:
            locations.append(address)

    if len(locations) >= 2:
        st.markdown("#### ⏳ Generating Routes from Real-World Distances")
        with st.spinner("Fetching distances and calculating route matrix..."):
            routes = auto_generate_routes(locations)

        if routes:
            st.success("✅ Distance matrix generated!")
            st.markdown("### 📦 Generated Route Matrix")
            df_routes = pd.DataFrame(routes, columns=["From", "To", "Distance (km)"])
            st.dataframe(df_routes, use_container_width=True)
        else:
            st.error("❌ Failed to generate routes. Please double-check address spelling.")

# =================== CSV UPLOAD ===================
elif input_mode == "Upload CSV":
    st.markdown("### 📄 Upload a CSV with a 'Location' Column")
    uploaded_file = st.file_uploader("Choose your CSV file", type=["csv"])

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.markdown("### 📊 Uploaded Data")
        st.dataframe(df, use_container_width=True)

        try:
            locations = df["Location"].dropna().tolist()

            if len(locations) >= 2:
                with st.spinner("Fetching distances and calculating route matrix..."):
                    routes = auto_generate_routes(locations)

                if routes:
                    st.success("✅ Distance matrix generated!")
                    st.markdown("### 📦 Generated Route Matrix")
                    df_routes = pd.DataFrame(routes, columns=["From", "To", "Distance (km)"])
                    st.dataframe(df_routes, use_container_width=True)
                else:
                    st.error("❌ Could not generate routes. Please verify your CSV format and addresses.")
            else:
                st.warning("⚠️ You need at least 2 valid locations in your file.")
        except Exception:
            st.error("❌ The CSV must contain a column named 'Location'.")

# =================== OPTIMIZE ROUTE ===================
if len(locations) >= 2 and len(routes) >= 1:
    st.markdown("## 🧠 Optimize the Route")

    source = st.selectbox("🏭 Select Starting Point (e.g., Warehouse)", options=locations)

    if st.button("🚀 Find Optimal Route"):
        citygraph = construct_graph(locations, routes)
        shortest_route, shortest_distance = find_best_route(citygraph, source)

        if shortest_route and shortest_distance is not None:
            st.success(f"✅ Optimal Route Found: {' ➡️ '.join(shortest_route)}")
            st.info(f"📏 Total Distance: **{shortest_distance:.2f} km**")

           # =================== ROUTE VISUALIZATION ===================
            st.markdown("### 📍 Optimized Route Graph")
            try:
                pos = nx.circular_layout(citygraph)

                fig, ax = plt.subplots(figsize=(10, 6))

                # Draw base nodes in light gray
                nx.draw_networkx_nodes(citygraph, pos, ax=ax, node_size=1400, node_color='lightgray', edgecolors='black')

                # Highlight nodes along the optimal route
                for i, node in enumerate(shortest_route):
                    if i == 0:
                        color = 'green'
                    elif i == len(shortest_route) - 1:
                        color = 'red'
                    else:
                        color = 'skyblue'
                    nx.draw_networkx_nodes(
                        citygraph, pos, nodelist=[node], ax=ax,
                        node_size=1600, node_color=color, edgecolors='black'
                    )

                # ✅ Use shortened labels (only first word of each address)
                short_labels = {node: node.split()[0] for node in citygraph.nodes()}
                nx.draw_networkx_labels(citygraph, pos, labels=short_labels, ax=ax, font_size=9, font_weight='bold')

                # All faded edges
                nx.draw_networkx_edges(citygraph, pos, ax=ax, alpha=0.3)

                # Highlight shortest route edges in red
                path_edges = list(zip(shortest_route, shortest_route[1:]))
                nx.draw_networkx_edges(
                    citygraph, pos, edgelist=path_edges, ax=ax,
                    edge_color='crimson', width=2.5, arrows=True, arrowsize=15
                )

                # Add edge labels for distances
                edge_labels = nx.get_edge_attributes(citygraph, 'weight')
                nx.draw_networkx_edge_labels(
                    citygraph, pos, edge_labels=edge_labels, ax=ax, font_size=8
                )

                ax.set_title("Optimized Delivery Route (Compact View)", fontsize=14)
                ax.axis('off')
                st.pyplot(fig)

            except Exception as e:
                st.error("⚠️ Error displaying the route map.")
                st.exception(e)

        else:
            st.error("❌ Could not compute the optimal route. Please check the input data.")
