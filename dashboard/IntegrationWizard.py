
import streamlit as st
import os
from monitoring.vcenter_monitor import fetch_vcenter_metrics
from monitoring.zabbix_connector import ZabbixConnector
from monitoring.prometheus_monitor import fetch_prometheus_metrics
from monitoring.store_metrics import store_metrics

st.set_page_config(page_title="IROA Integration Wizard", layout="centered")

st.title("🔧 IROA Integration Wizard")

option = st.selectbox("Choose system to integrate", ["vCenter", "Zabbix", "Prometheus"])

st.divider()

if option == "vCenter":
    st.subheader("VMware vCenter Integration")
    host = st.text_input("vCenter Host", "vcenter.local")
    user = st.text_input("Username", "administrator@vsphere.local")
    pwd = st.text_input("Password", type="password")

    if st.button("Test vCenter Connection & Ingest"):
        try:
            fetch_vcenter_metrics(host, user, pwd)
            st.success("✅ vCenter integration successful!")
        except Exception as e:
            st.error(f"❌ Failed to connect to vCenter: {e}")

elif option == "Zabbix":
    st.subheader("Zabbix Integration")
    url = st.text_input("Zabbix API URL", "http://zabbix.local/api_jsonrpc.php")
    user = st.text_input("Username", "Admin")
    pwd = st.text_input("Password", type="password")

    if st.button("Test Zabbix Connection & Ingest"):
        try:
            connector = ZabbixConnector(url, user, pwd)
            connector.ingest_zabbix_metrics()
            st.success("✅ Zabbix metrics imported successfully!")
        except Exception as e:
            st.error(f"❌ Failed to connect to Zabbix: {e}")

elif option == "Prometheus":
    st.subheader("Prometheus Integration")
    prom_url = st.text_input("Prometheus URL", "http://localhost:9090")

    if st.button("Test Prometheus Connection & Ingest"):
        try:
            os.environ["PROMETHEUS_URL"] = prom_url
            metrics = fetch_prometheus_metrics()
            store_metrics(metrics)
            st.success(f"✅ Ingested {len(metrics)} Prometheus samples.")
        except Exception as e:
            st.error(f"❌ Failed to pull from Prometheus: {e}")
