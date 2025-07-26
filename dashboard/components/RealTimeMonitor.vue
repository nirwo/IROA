<template>
  <div class="bg-white rounded-xl shadow-sm p-6">
    <div class="flex items-center justify-between mb-6">
      <h3 class="text-lg font-semibold">Real-Time Monitoring</h3>
      <div class="flex items-center space-x-2">
        <div :class="[
          'w-2 h-2 rounded-full',
          isConnected ? 'bg-green-400 animate-pulse' : 'bg-red-400'
        ]"></div>
        <span class="text-sm text-gray-600">
          {{ isConnected ? 'Live' : 'Disconnected' }}
        </span>
      </div>
    </div>
    
    <!-- Real-time metrics grid -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
      <div class="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-4">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Avg CPU</p>
            <p class="text-2xl font-bold text-indigo-600">{{ metrics.avgCpu }}%</p>
          </div>
          <div class="w-10 h-10 bg-indigo-100 rounded-lg flex items-center justify-center">
            <i data-lucide="cpu" class="w-5 h-5 text-indigo-600"></i>
          </div>
        </div>
      </div>
      
      <div class="bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg p-4">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Avg Memory</p>
            <p class="text-2xl font-bold text-green-600">{{ metrics.avgMemory }}%</p>
          </div>
          <div class="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
            <i data-lucide="memory-stick" class="w-5 h-5 text-green-600"></i>
          </div>
        </div>
      </div>
      
      <div class="bg-gradient-to-r from-purple-50 to-violet-50 rounded-lg p-4">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Active VMs</p>
            <p class="text-2xl font-bold text-purple-600">{{ metrics.activeVMs }}</p>
          </div>
          <div class="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
            <i data-lucide="server" class="w-5 h-5 text-purple-600"></i>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Real-time chart -->
    <div class="h-64">
      <canvas ref="realtimeChart"></canvas>
    </div>
    
    <!-- Recent events -->
    <div class="mt-6">
      <h4 class="text-sm font-medium text-gray-900 mb-3">Recent Events</h4>
      <div class="space-y-2 max-h-32 overflow-y-auto">
        <div v-for="event in recentEvents" :key="event.id" class="flex items-center space-x-3 text-sm">
          <div :class="[
            'w-2 h-2 rounded-full',
            event.type === 'warning' ? 'bg-yellow-400' : 
            event.type === 'error' ? 'bg-red-400' : 'bg-green-400'
          ]"></div>
          <span class="text-gray-600">{{ event.timestamp }}</span>
          <span class="flex-1">{{ event.message }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'RealTimeMonitor',
  data() {
    return {
      isConnected: true,
      metrics: {
        avgCpu: 45,
        avgMemory: 62,
        activeVMs: 5
      },
      recentEvents: [
        { id: 1, type: 'info', timestamp: '09:30:15', message: 'VM web-server-01 CPU usage normalized' },
        { id: 2, type: 'warning', timestamp: '09:28:42', message: 'High memory usage detected on db-server-01' },
        { id: 3, type: 'info', timestamp: '09:25:33', message: 'Optimization recommendation applied' },
        { id: 4, type: 'info', timestamp: '09:22:18', message: 'System health check completed' }
      ],
      updateInterval: null,
      chartData: {
        cpu: [45, 47, 44, 46, 48, 45, 43, 45],
        memory: [62, 64, 61, 63, 65, 62, 60, 62],
        timestamps: []
      }
    }
  },
  mounted() {
    this.initializeChart()
    this.startRealTimeUpdates()
    
    // Initialize Lucide icons
    if (window.lucide) {
      window.lucide.createIcons()
    }
  },
  beforeUnmount() {
    if (this.updateInterval) {
      clearInterval(this.updateInterval)
    }
  },
  methods: {
    initializeChart() {
      const ctx = this.$refs.realtimeChart
      if (!ctx) return
      
      // Generate initial timestamps
      const now = new Date()
      this.chartData.timestamps = Array.from({ length: 8 }, (_, i) => {
        const time = new Date(now.getTime() - (7 - i) * 30000) // 30 second intervals
        return time.toLocaleTimeString()
      })
      
      this.chart = new Chart(ctx, {
        type: 'line',
        data: {
          labels: this.chartData.timestamps,
          datasets: [{
            label: 'CPU %',
            data: this.chartData.cpu,
            borderColor: 'rgb(99, 102, 241)',
            backgroundColor: 'rgba(99, 102, 241, 0.1)',
            tension: 0.4,
            fill: false
          }, {
            label: 'Memory %',
            data: this.chartData.memory,
            borderColor: 'rgb(34, 197, 94)',
            backgroundColor: 'rgba(34, 197, 94, 0.1)',
            tension: 0.4,
            fill: false
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          animation: {
            duration: 750
          },
          plugins: {
            legend: {
              position: 'top'
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              max: 100
            },
            x: {
              display: true
            }
          }
        }
      })
    },
    startRealTimeUpdates() {
      this.updateInterval = setInterval(() => {
        this.updateMetrics()
        this.updateChart()
      }, 5000) // Update every 5 seconds
    },
    updateMetrics() {
      // Simulate real-time data updates
      this.metrics.avgCpu = Math.max(0, Math.min(100, this.metrics.avgCpu + (Math.random() - 0.5) * 10))
      this.metrics.avgMemory = Math.max(0, Math.min(100, this.metrics.avgMemory + (Math.random() - 0.5) * 8))
      
      // Occasionally add new events
      if (Math.random() < 0.3) {
        const eventTypes = ['info', 'warning', 'error']
        const messages = [
          'VM performance optimized',
          'Resource threshold exceeded',
          'Anomaly detected in network traffic',
          'Backup process completed',
          'CPU spike detected'
        ]
        
        const newEvent = {
          id: Date.now(),
          type: eventTypes[Math.floor(Math.random() * eventTypes.length)],
          timestamp: new Date().toLocaleTimeString(),
          message: messages[Math.floor(Math.random() * messages.length)]
        }
        
        this.recentEvents.unshift(newEvent)
        if (this.recentEvents.length > 10) {
          this.recentEvents.pop()
        }
      }
    },
    updateChart() {
      if (!this.chart) return
      
      // Add new data point
      const newCpu = Math.max(0, Math.min(100, this.chartData.cpu[this.chartData.cpu.length - 1] + (Math.random() - 0.5) * 10))
      const newMemory = Math.max(0, Math.min(100, this.chartData.memory[this.chartData.memory.length - 1] + (Math.random() - 0.5) * 8))
      const newTimestamp = new Date().toLocaleTimeString()
      
      // Update data arrays
      this.chartData.cpu.push(newCpu)
      this.chartData.memory.push(newMemory)
      this.chartData.timestamps.push(newTimestamp)
      
      // Keep only last 8 data points
      if (this.chartData.cpu.length > 8) {
        this.chartData.cpu.shift()
        this.chartData.memory.shift()
        this.chartData.timestamps.shift()
      }
      
      // Update chart
      this.chart.data.labels = this.chartData.timestamps
      this.chart.data.datasets[0].data = this.chartData.cpu
      this.chart.data.datasets[1].data = this.chartData.memory
      this.chart.update('none') // No animation for real-time updates
    }
  }
}
</script>
