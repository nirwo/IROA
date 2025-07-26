
import streamlit as st
import requests

st.set_page_config(page_title="IROA Assistant", layout="wide")

st.title("💡 IROA Chatbot Assistant")
st.markdown("Ask for suggestions to optimize your virtual resources.")

user_input = st.text_input("Ask a question", placeholder="e.g., Which VMs are underutilized?")

if user_input:
    if "underutilized" in user_input.lower() or "recommend" in user_input.lower():
        try:
            response = requests.get("http://localhost:8001/recommendations")
            if response.status_code == 200:
                suggestions = response.json()
                if suggestions:
                    for rec in suggestions:
                        st.success(f"💬 {rec['vm']} - {rec['suggestion']}")
                else:
                    st.warning("No recommendations found at the moment.")
            else:
                st.error("Failed to fetch recommendations from API")
        except Exception as e:
            st.error(f"Error connecting to API: {e}")
    else:
        st.info("Try asking about underutilized VMs or cost-saving tips.")
