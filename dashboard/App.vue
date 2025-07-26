
<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <header class="gradient-bg text-white shadow-lg">
      <div class="container mx-auto px-6 py-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-3">
            <div class="w-10 h-10 bg-white bg-opacity-20 rounded-lg flex items-center justify-center">
              <i data-lucide="brain-circuit" class="w-6 h-6"></i>
            </div>
            <div>
              <h1 class="text-2xl font-bold">IROA</h1>
              <p class="text-sm opacity-90">Intelligent Resource Optimization Agent</p>
            </div>
          </div>
          <div class="flex items-center space-x-4">
            <div class="flex items-center space-x-2 bg-white bg-opacity-20 px-3 py-2 rounded-lg">
              <div class="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
              <span class="text-sm">System Online</span>
            </div>
            <button @click="refreshData" class="bg-white bg-opacity-20 hover:bg-opacity-30 px-4 py-2 rounded-lg transition-all">
              <i data-lucide="refresh-cw" class="w-4 h-4"></i>
            </button>
          </div>
        </div>
      </div>
    </header>

    <!-- Navigation -->
    <nav class="bg-white shadow-sm border-b">
      <div class="container mx-auto px-6">
        <div class="flex space-x-8">
          <button 
            v-for="tab in tabs" 
            :key="tab.id"
            @click="activeTab = tab.id"
            :class="[
              'py-4 px-2 border-b-2 font-medium text-sm transition-colors',
              activeTab === tab.id 
                ? 'border-indigo-500 text-indigo-600' 
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            <i :data-lucide="tab.icon" class="w-4 h-4 inline mr-2"></i>
            {{ tab.name }}
          </button>
        </div>
      </div>
    </nav>

    <!-- Main Content -->
    <main class="container mx-auto px-6 py-8">
      <!-- Overview Tab -->
      <div v-if="activeTab === 'overview'" class="space-y-6">
        <!-- Stats Cards -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div v-for="stat in stats" :key="stat.title" class="bg-white rounded-xl shadow-sm p-6 card-hover">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm font-medium text-gray-600">{{ stat.title }}</p>
                <p class="text-2xl font-bold text-gray-900">{{ stat.value }}</p>
                <p :class="['text-sm', stat.change >= 0 ? 'text-green-600' : 'text-red-600']">
                  {{ stat.change >= 0 ? '+' : '' }}{{ stat.change }}%
                </p>
              </div>
              <div :class="['w-12 h-12 rounded-lg flex items-center justify-center', stat.bgColor]">
                <i :data-lucide="stat.icon" class="w-6 h-6 text-white"></i>
              </div>
            </div>
          </div>
        </div>

        <!-- Charts Row -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <!-- Resource Usage Chart -->
          <div class="bg-white rounded-xl shadow-sm p-6">
            <h3 class="text-lg font-semibold mb-4">Resource Usage Trends</h3>
            <div class="h-64 relative">
              <canvas ref="usageChart" class="w-full h-full"></canvas>
            </div>
          </div>
          
          <!-- VM Distribution -->
          <div class="bg-white rounded-xl shadow-sm p-6">
            <h3 class="text-lg font-semibold mb-4">VM Distribution by Cluster</h3>
            <div class="h-64 relative">
              <canvas ref="distributionChart" class="w-full h-full"></canvas>
            </div>
          </div>
        </div>
      </div>

      <!-- Recommendations Tab -->
      <div v-if="activeTab === 'recommendations'" class="space-y-6">
        <div class="bg-white rounded-xl shadow-sm p-6">
          <div class="flex items-center justify-between mb-6">
            <h2 class="text-xl font-semibold">Optimization Recommendations</h2>
            <span class="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium">
              {{ recommendations.length }} Active
            </span>
          </div>
          
          <div v-if="loading" class="flex items-center justify-center py-12">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
            <span class="ml-3 text-gray-600">Loading recommendations...</span>
          </div>
          
          <div v-else-if="recommendations.length" class="space-y-4">
            <div 
              v-for="rec in recommendations" 
              :key="rec.vm" 
              class="border border-gray-200 rounded-lg p-4 hover:border-indigo-300 transition-colors"
            >
              <div class="flex items-start justify-between">
                <div class="flex-1">
                  <div class="flex items-center space-x-3 mb-2">
                    <div class="w-3 h-3 bg-yellow-400 rounded-full"></div>
                    <h3 class="font-semibold text-gray-900">{{ rec.vm }}</h3>
                    <span class="bg-gray-100 text-gray-700 px-2 py-1 rounded text-xs">{{ rec.reason }}</span>
                  </div>
                  <p class="text-gray-600 mb-3">{{ rec.suggestion }}</p>
                  <div class="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span class="text-gray-500">Avg CPU:</span>
                      <span class="font-medium ml-1">{{ rec.details.avg_cpu }}%</span>
                    </div>
                    <div>
                      <span class="text-gray-500">Avg Memory:</span>
                      <span class="font-medium ml-1">{{ rec.details.avg_mem }}%</span>
                    </div>
                  </div>
                </div>
                <div class="flex space-x-2">
                  <button class="bg-indigo-600 text-white px-3 py-1 rounded text-sm hover:bg-indigo-700 transition-colors">
                    Apply
                  </button>
                  <button class="bg-gray-200 text-gray-700 px-3 py-1 rounded text-sm hover:bg-gray-300 transition-colors">
                    Dismiss
                  </button>
                </div>
              </div>
            </div>
          </div>
          
          <div v-else class="text-center py-12">
            <i data-lucide="check-circle" class="w-12 h-12 text-green-500 mx-auto mb-3"></i>
            <h3 class="text-lg font-medium text-gray-900 mb-2">All Optimized!</h3>
            <p class="text-gray-600">No optimization recommendations at this time.</p>
          </div>
        </div>
      </div>

      <!-- VMs Tab -->
      <div v-if="activeTab === 'vms'" class="space-y-6">
        <div class="bg-white rounded-xl shadow-sm p-6">
          <div class="flex items-center justify-between mb-6">
            <h2 class="text-xl font-semibold">Virtual Machines</h2>
            <div class="flex space-x-3">
              <input 
                v-model="searchTerm" 
                placeholder="Search VMs..." 
                class="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              >
              <select 
                v-model="filterStatus" 
                class="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              >
                <option value="all">All Status</option>
                <option value="running">Running</option>
                <option value="stopped">Stopped</option>
                <option value="underutilized">Underutilized</option>
              </select>
              <div class="flex bg-gray-100 rounded-lg p-1">
                <button 
                  @click="viewMode = 'grid'"
                  :class="[
                    'px-3 py-1 rounded text-sm font-medium transition-colors',
                    viewMode === 'grid' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-600 hover:text-gray-900'
                  ]"
                >
                  <i data-lucide="grid-3x3" class="w-4 h-4"></i>
                </button>
                <button 
                  @click="viewMode = 'table'"
                  :class="[
                    'px-3 py-1 rounded text-sm font-medium transition-colors',
                    viewMode === 'table' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-600 hover:text-gray-900'
                  ]"
                >
                  <i data-lucide="list" class="w-4 h-4"></i>
                </button>
              </div>
            </div>
          </div>
          
          <!-- Grid View -->
          <div v-if="viewMode === 'grid'" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div v-for="vm in filteredVMs" :key="vm.name" class="bg-gradient-to-br from-white to-gray-50 rounded-xl shadow-sm p-6 card-hover border border-gray-200">
              <div class="flex items-center justify-between mb-4">
                <div class="flex items-center space-x-3">
                  <div class="w-12 h-12 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-lg flex items-center justify-center">
                    <i data-lucide="server" class="w-6 h-6 text-white"></i>
                  </div>
                  <div>
                    <h3 class="font-semibold text-gray-900">{{ vm.name }}</h3>
                    <p class="text-sm text-gray-500">{{ vm.cluster }}</p>
                  </div>
                </div>
                <span :class="[
                  'inline-flex px-2 py-1 text-xs font-semibold rounded-full',
                  vm.status === 'running' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                ]">
                  {{ vm.status }}
                </span>
              </div>
              
              <!-- Resource Usage -->
              <div class="space-y-3 mb-4">
                <div>
                  <div class="flex justify-between text-sm mb-1">
                    <span class="text-gray-600">CPU Usage</span>
                    <span class="font-medium">{{ vm.cpu }}%</span>
                  </div>
                  <div class="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      :class="[
                        'h-2 rounded-full transition-all duration-300',
                        vm.cpu < 30 ? 'bg-green-500' : vm.cpu < 70 ? 'bg-yellow-500' : 'bg-red-500'
                      ]"
                      :style="{ width: vm.cpu + '%' }"
                    ></div>
                  </div>
                </div>
                
                <div>
                  <div class="flex justify-between text-sm mb-1">
                    <span class="text-gray-600">Memory Usage</span>
                    <span class="font-medium">{{ vm.memory_usage }}%</span>
                  </div>
                  <div class="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      :class="[
                        'h-2 rounded-full transition-all duration-300',
                        vm.memory_usage < 50 ? 'bg-green-500' : vm.memory_usage < 80 ? 'bg-yellow-500' : 'bg-red-500'
                      ]"
                      :style="{ width: vm.memory_usage + '%' }"
                    ></div>
                  </div>
                </div>
              </div>
              
              <!-- VM Specs -->
              <div class="mb-4 pt-4 border-t border-gray-100">
                <div class="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span class="text-gray-500">CPU Cores:</span>
                    <span class="font-medium ml-1">{{ vm.cores }}</span>
                  </div>
                  <div>
                    <span class="text-gray-500">Memory:</span>
                    <span class="font-medium ml-1">{{ vm.memory }}GB</span>
                  </div>
                </div>
              </div>
              
              <!-- Actions -->
              <div class="flex space-x-2">
                <button 
                  @click="viewVMDetails(vm)"
                  class="flex-1 bg-indigo-600 text-white px-3 py-2 rounded-lg text-sm font-medium hover:bg-indigo-700 transition-colors"
                >
                  View Details
                </button>
                <button 
                  @click="getVMForecast(vm.id)"
                  class="flex-1 bg-gray-100 text-gray-700 px-3 py-2 rounded-lg text-sm font-medium hover:bg-gray-200 transition-colors"
                >
                  Forecast
                </button>
              </div>
            </div>
          </div>
          
          <!-- Table View -->
          <div v-else class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">VM Name</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">CPU Usage</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Memory</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Cluster</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="vm in filteredVMs" :key="vm.name" class="hover:bg-gray-50">
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="flex items-center">
                      <div class="w-8 h-8 bg-indigo-100 rounded-lg flex items-center justify-center mr-3">
                        <i data-lucide="server" class="w-4 h-4 text-indigo-600"></i>
                      </div>
                      <div>
                        <div class="text-sm font-medium text-gray-900">{{ vm.name }}</div>
                        <div class="text-sm text-gray-500">{{ vm.cores }} cores, {{ vm.memory }}GB RAM</div>
                      </div>
                    </div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <span :class="[
                      'inline-flex px-2 py-1 text-xs font-semibold rounded-full',
                      vm.status === 'running' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    ]">
                      {{ vm.status }}
                    </span>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="flex items-center">
                      <div class="w-16 bg-gray-200 rounded-full h-2 mr-2">
                        <div 
                          :class="[
                            'h-2 rounded-full',
                            vm.cpu < 30 ? 'bg-green-500' : vm.cpu < 70 ? 'bg-yellow-500' : 'bg-red-500'
                          ]"
                          :style="{ width: vm.cpu + '%' }"
                        ></div>
                      </div>
                      <span class="text-sm text-gray-600">{{ vm.cpu }}%</span>
                    </div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="flex items-center">
                      <div class="w-16 bg-gray-200 rounded-full h-2 mr-2">
                        <div 
                          :class="[
                            'h-2 rounded-full',
                            vm.memory_usage < 50 ? 'bg-green-500' : vm.memory_usage < 80 ? 'bg-yellow-500' : 'bg-red-500'
                          ]"
                          :style="{ width: vm.memory_usage + '%' }"
                        ></div>
                      </div>
                      <span class="text-sm text-gray-600">{{ vm.memory_usage }}%</span>
                    </div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">{{ vm.cluster }}</td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button @click="viewVMDetails(vm)" class="text-indigo-600 hover:text-indigo-900 mr-3">View</button>
                    <button @click="getVMForecast(vm.id)" class="text-green-600 hover:text-green-900">Forecast</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Analytics Tab -->
      <div v-if="activeTab === 'analytics'" class="space-y-6">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <!-- Forecast Chart -->
          <div class="bg-white rounded-xl shadow-sm p-6">
            <h3 class="text-lg font-semibold mb-4">CPU Usage Forecast</h3>
            <div v-if="selectedVM">
              <p class="text-sm text-gray-600 mb-4">24-hour prediction for {{ selectedVM.name }}</p>
              <div class="h-64 relative">
                <canvas ref="forecastChart" class="w-full h-full"></canvas>
              </div>
            </div>
            <div v-else class="flex items-center justify-center h-64 text-gray-500">
              <div class="text-center">
                <i data-lucide="trending-up" class="w-12 h-12 mx-auto mb-3 opacity-50"></i>
                <p>Select a VM to view forecast</p>
              </div>
            </div>
          </div>
          
          <!-- Anomalies -->
          <div class="bg-white rounded-xl shadow-sm p-6">
            <h3 class="text-lg font-semibold mb-4">Anomaly Detection</h3>
            <div v-if="anomalies.length" class="space-y-3">
              <div v-for="anomaly in anomalies" :key="anomaly.index" class="border-l-4 border-red-400 pl-4 py-2">
                <div class="flex items-center justify-between">
                  <div>
                    <p class="text-sm font-medium text-gray-900">Unusual Pattern Detected</p>
                    <p class="text-xs text-gray-600">{{ formatDate(anomaly.timestamp) }}</p>
                  </div>
                  <div class="text-right text-xs text-gray-600">
                    <div>CPU: {{ anomaly.cpu.toFixed(1) }}%</div>
                    <div>Memory: {{ anomaly.memory.toFixed(1) }}%</div>
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="flex items-center justify-center h-64 text-gray-500">
              <div class="text-center">
                <i data-lucide="shield-check" class="w-12 h-12 mx-auto mb-3 opacity-50"></i>
                <p>No anomalies detected</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
export default {
  data() {
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
        { id: 'analytics', name: 'Analytics', icon: 'bar-chart-3' }
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
      ]
    }
  },
  computed: {
    filteredVMs() {
      let vms = this.mockVMs
      
      if (this.searchTerm) {
        vms = vms.filter(vm => 
          vm.name.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
          vm.cluster.toLowerCase().includes(this.searchTerm.toLowerCase())
        )
      }
      
      if (this.filterStatus !== 'all') {
        if (this.filterStatus === 'underutilized') {
          vms = vms.filter(vm => vm.cpu < 10 && vm.memory_usage < 20)
        } else {
          vms = vms.filter(vm => vm.status === this.filterStatus)
        }
      }
      
      return vms
    }
  },
  async mounted() {
    try {
      await this.loadData()
      // Wait for DOM to be ready before initializing charts
      this.$nextTick(() => {
        this.initializeCharts()
      })
      // Initialize Lucide icons
      if (window.lucide) {
        window.lucide.createIcons()
      }
    } catch (error) {
      console.error('Error during component mounting:', error)
    }
  },
  beforeUnmount() {
    // Clean up charts to prevent memory leaks
    if (this.usageChart) {
      this.usageChart.destroy()
    }
    if (this.distributionChart) {
      this.distributionChart.destroy()
    }
    if (this.forecastChart) {
      this.forecastChart.destroy()
    }
  },
  methods: {
    async loadData() {
      this.loading = true
      try {
        // Load recommendations
        const recRes = await fetch('http://localhost:8001/recommendations')
        if (recRes.ok) {
          this.recommendations = await recRes.json()
        } else {
          console.warn('Failed to load recommendations:', recRes.status)
          this.recommendations = []
        }
        
        // Load underutilized VMs
        const underRes = await fetch('http://localhost:8001/underutilized')
        if (underRes.ok) {
          this.underutilizedVMs = await underRes.json()
          // Update stats
          this.stats[1].value = this.underutilizedVMs.length.toString()
        } else {
          console.warn('Failed to load underutilized VMs:', underRes.status)
          this.underutilizedVMs = []
        }
      } catch (error) {
        console.error('Error loading data:', error)
        // Set default values on error
        this.recommendations = []
        this.underutilizedVMs = []
      } finally {
        this.loading = false
      }
    },
    async refreshData() {
      await this.loadData()
      this.initializeCharts()
    },
    async getVMForecast(vmId) {
      try {
        const res = await fetch(`http://localhost:8001/forecast/${vmId}`)
        if (res.ok) {
          const data = await res.json()
          this.forecast = data.cpu_forecast || []
          this.selectedVM = this.mockVMs.find(vm => vm.id === vmId)
          this.activeTab = 'analytics'
          
          // Update forecast chart
          this.$nextTick(() => {
            this.initializeForecastChart()
          })
        } else {
          console.warn('Failed to load forecast:', res.status)
          this.forecast = []
        }
      } catch (error) {
        console.error('Error loading forecast:', error)
        this.forecast = []
      }
    },
    async getAnomalies(vmId) {
      try {
        const res = await fetch(`http://localhost:8001/anomalies/${vmId}`)
        const data = await res.json()
        this.anomalies = data.anomalies || []
      } catch (error) {
        console.error('Error loading anomalies:', error)
      }
    },
    viewVMDetails(vm) {
      this.selectedVM = vm
      this.getVMForecast(vm.id)
      this.getAnomalies(vm.id)
    },
    formatDate(dateString) {
      return new Date(dateString).toLocaleString()
    },
    initializeCharts() {
      try {
        this.initializeUsageChart()
        this.initializeDistributionChart()
      } catch (error) {
        console.error('Error initializing charts:', error)
      }
    },
    initializeUsageChart() {
      const ctx = this.$refs.usageChart
      if (!ctx) return
      
      // Destroy existing chart if it exists
      if (this.usageChart) {
        this.usageChart.destroy()
      }
      
      this.usageChart = new Chart(ctx, {
        type: 'line',
        data: {
          labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'],
          datasets: [{
            label: 'CPU Usage',
            data: [30, 45, 60, 55, 70, 45],
            borderColor: 'rgb(99, 102, 241)',
            backgroundColor: 'rgba(99, 102, 241, 0.1)',
            tension: 0.4
          }, {
            label: 'Memory Usage',
            data: [40, 35, 50, 65, 60, 55],
            borderColor: 'rgb(34, 197, 94)',
            backgroundColor: 'rgba(34, 197, 94, 0.1)',
            tension: 0.4
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'top'
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              max: 100
            }
          }
        }
      })
    },
    initializeDistributionChart() {
      const ctx = this.$refs.distributionChart
      if (!ctx) return
      
      // Destroy existing chart if it exists
      if (this.distributionChart) {
        this.distributionChart.destroy()
      }
      
      this.distributionChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: ['Production', 'Development', 'Testing', 'Backup'],
          datasets: [{
            data: [2, 1, 1, 1],
            backgroundColor: [
              'rgb(99, 102, 241)',
              'rgb(34, 197, 94)',
              'rgb(251, 191, 36)',
              'rgb(239, 68, 68)'
            ]
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'bottom'
            }
          }
        }
      })
    },
    initializeForecastChart() {
      const ctx = this.$refs.forecastChart
      if (!ctx || !this.forecast.length) return
      
      // Destroy existing chart if it exists
      if (this.forecastChart) {
        this.forecastChart.destroy()
      }
      
      const hours = Array.from({ length: 24 }, (_, i) => `${i}:00`)
      
      this.forecastChart = new Chart(ctx, {
        type: 'line',
        data: {
          labels: hours,
          datasets: [{
            label: 'Predicted CPU Usage',
            data: this.forecast,
            borderColor: 'rgb(168, 85, 247)',
            backgroundColor: 'rgba(168, 85, 247, 0.1)',
            tension: 0.4,
            fill: true
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'top'
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              max: 100
            }
          }
        }
      })
    }
  }
}
</script>
