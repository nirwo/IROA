
// Use global Vue from CDN
const { createApp } = Vue;

// Import the App component (we'll need to convert this to a global object)
fetch('./App.vue')
  .then(response => response.text())
  .then(vueContent => {
    // Parse the Vue SFC content and create the app
    const app = createApp({
      template: `<div id="app">${extractTemplate(vueContent)}</div>`,
      data() {
        return extractData(vueContent);
      },
      methods: extractMethods(vueContent),
      computed: extractComputed(vueContent),
      mounted() {
        this.loadData();
        this.$nextTick(() => {
          this.initializeCharts();
        });
      },
      beforeUnmount() {
        if (this.usageChart) {
          this.usageChart.destroy();
        }
        if (this.distributionChart) {
          this.distributionChart.destroy();
        }
        if (this.forecastChart) {
          this.forecastChart.destroy();
        }
      }
    });
    
    app.mount('#app');
  })
  .catch(error => {
    console.error('Error loading Vue app:', error);
    // Fallback: create a simple app
    createSimpleApp();
  });

function createSimpleApp() {
  const app = createApp({
    template: `
      <div class="min-h-screen bg-gray-50">
        <div class="container mx-auto px-6 py-8">
          <h1 class="text-3xl font-bold text-gray-900 mb-8">IROA Dashboard</h1>
          <div class="bg-white rounded-xl shadow-sm p-6">
            <p class="text-gray-600">Loading dashboard components...</p>
            <div class="mt-4">
              <button @click="testAPI" class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
                Test API Connection
              </button>
            </div>
            <div v-if="apiStatus" class="mt-4 p-4 rounded-md" :class="apiStatus.success ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'">
              {{ apiStatus.message }}
            </div>
          </div>
        </div>
      </div>
    `,
    data() {
      return {
        apiStatus: null
      };
    },
    methods: {
      async testAPI() {
        try {
          const response = await fetch('http://localhost:8001/health');
          const data = await response.json();
          this.apiStatus = {
            success: true,
            message: `API is working! Status: ${data.status}`
          };
        } catch (error) {
          this.apiStatus = {
            success: false,
            message: `API connection failed: ${error.message}`
          };
        }
      }
    }
  });
  
  app.mount('#app');
}

// Helper functions to parse Vue SFC (simplified)
function extractTemplate(vueContent) {
  const templateMatch = vueContent.match(/<template[^>]*>([\s\S]*?)<\/template>/);
  return templateMatch ? templateMatch[1].trim() : '<div>Error loading template</div>';
}

function extractData(vueContent) {
  // This is a simplified parser - in a real app you'd use a proper SFC parser
  return {
    activeTab: 'overview',
    loading: false,
    searchTerm: '',
    filterStatus: 'all',
    viewMode: 'grid',
    selectedVM: null,
    recommendations: [],
    underutilizedVMs: [],
    anomalies: [],
    forecast: [],
    tabs: [
      { id: 'overview', name: 'Overview', icon: 'layout-dashboard' },
      { id: 'recommendations', name: 'Recommendations', icon: 'lightbulb' },
      { id: 'vms', name: 'Virtual Machines', icon: 'server' },
      { id: 'analytics', name: 'Analytics', icon: 'bar-chart-3' },
      { id: 'admin', name: 'Administration', icon: 'settings' }
    ],
    stats: [
      { title: 'Total VMs', value: '5', change: 0, icon: 'server', bgColor: 'bg-blue-500' },
      { title: 'Underutilized', value: '2', change: -20, icon: 'trending-down', bgColor: 'bg-yellow-500' },
      { title: 'Cost Savings', value: '$1,240', change: 15, icon: 'dollar-sign', bgColor: 'bg-green-500' },
      { title: 'Efficiency', value: '87%', change: 5, icon: 'zap', bgColor: 'bg-purple-500' }
    ],
    mockVMs: [
      { id: 1, name: 'web-server-01', status: 'running', cpu: 45, memory_usage: 62, cores: 4, memory: 8, cluster: 'prod-cluster' },
      { id: 2, name: 'db-server-01', status: 'running', cpu: 78, memory_usage: 85, cores: 8, memory: 32, cluster: 'prod-cluster' },
      { id: 3, name: 'test-vm-01', status: 'running', cpu: 5, memory_usage: 17, cores: 2, memory: 4, cluster: 'test-cluster' },
      { id: 4, name: 'backup-vm-01', status: 'running', cpu: 5, memory_usage: 17, cores: 2, memory: 4, cluster: 'backup-cluster' },
      { id: 5, name: 'dev-server-01', status: 'running', cpu: 32, memory_usage: 48, cores: 4, memory: 16, cluster: 'dev-cluster' }
    ],
    adminData: {
      selectedIntegration: 'mac',
      macMonitoring: {
        isRunning: false,
        interval: 30,
        lastUpdate: null,
        systemInfo: null,
        currentStats: null
      },
      integrationOptions: [
        { id: 'mac', name: 'Mac System', icon: '🍎', description: 'Monitor your Mac system resources' },
        { id: 'vcenter', name: 'VMware vCenter', icon: '🏢', description: 'Connect to VMware vCenter Server' },
        { id: 'zabbix', name: 'Zabbix', icon: '📊', description: 'Integrate with Zabbix monitoring' },
        { id: 'prometheus', name: 'Prometheus', icon: '🔥', description: 'Connect to Prometheus metrics' }
      ],
      connectionForms: {
        vcenter: { host: 'vcenter.local', username: 'administrator@vsphere.local', password: '' },
        zabbix: { url: 'http://zabbix.local/api_jsonrpc.php', username: 'Admin', password: '' },
        prometheus: { url: 'http://localhost:9090' }
      }
    }
  };
}

function extractMethods(vueContent) {
  return {
    async loadData() {
      console.log('Loading data...');
      // Simplified data loading
    },
    initializeCharts() {
      console.log('Initializing charts...');
      // Simplified chart initialization
    }
  };
}

function extractComputed(vueContent) {
  return {
    filteredVMs() {
      return this.mockVMs;
    }
  };
}
