
import streamlit as st
import os
import subprocess
import threading
from monitoring.vcenter_monitor import fetch_vcenter_metrics
from monitoring.zabbix_connector import ZabbixConnector
from monitoring.prometheus_monitor import fetch_prometheus_metrics
from monitoring.store_metrics import store_metrics
from monitoring.mac_monitor import MacSystemMonitor

st.set_page_config(page_title="IROA Integration Wizard", layout="centered")

st.title("🔧 IROA Integration Wizard")

option = st.selectbox("Choose system to integrate", ["Mac System", "vCenter", "Zabbix", "Prometheus"])

st.divider()

if option == "Mac System":
    st.subheader("🍎 Mac System Integration")
    st.info("This will monitor your Mac system resources and create virtual VMs based on running processes.")
    
    interval = st.slider("Monitoring Interval (seconds)", min_value=10, max_value=300, value=30)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🚀 Start Mac Monitoring", type="primary"):
            try:
                monitor = MacSystemMonitor()
                # Create initial VMs
                monitor.create_virtual_vms()
                # Collect initial metrics
                metrics = monitor.collect_metrics()
                st.success(f"✅ Mac monitoring started! Collected metrics for {metrics['vm_count']} VMs")
                st.json({
                    'system_cpu': f"{metrics['system_cpu']:.1f}%",
                    'system_memory': f"{metrics['system_memory']:.1f}%",
                    'vm_count': metrics['vm_count']
                })
            except Exception as e:
                st.error(f"❌ Failed to start Mac monitoring: {e}")
    
    with col2:
        if st.button("📊 View Current Stats"):
            try:
                monitor = MacSystemMonitor()
                system_info = monitor.get_system_info()
                st.info(f"**Model:** {system_info['model']}\n**CPU:** {system_info['cpu']}\n**Memory:** {system_info['memory']}")
                
                cpu = monitor.get_cpu_usage()
                memory = monitor.get_memory_usage()
                disk = monitor.get_disk_usage()
                
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric("CPU Usage", f"{cpu:.1f}%")
                with col_b:
                    st.metric("Memory Usage", f"{memory:.1f}%")
                with col_c:
                    st.metric("Disk Usage", f"{disk:.1f}%")
                    
            except Exception as e:
                st.error(f"❌ Error getting system stats: {e}")

elif option == "vCenter":
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
