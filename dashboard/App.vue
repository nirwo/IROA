
<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Login Screen -->
    <div v-if="!isAuthenticated" class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex flex-col">
      <!-- Header -->
      <header class="gradient-bg text-white shadow-lg">
        <div class="container mx-auto px-6 py-4">
          <div class="flex items-center justify-center">
            <div class="flex items-center space-x-3">
              <div class="w-10 h-10 bg-white bg-opacity-20 rounded-lg flex items-center justify-center">
                <i data-lucide="brain-circuit" class="w-6 h-6"></i>
              </div>
              <div>
                <h1 class="text-2xl font-bold">IROA</h1>
                <p class="text-sm opacity-90">Intelligent Resource Optimization Agent</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      <!-- Main Login Content -->
      <main class="flex-1 flex items-center justify-center px-6 py-12">
        <div class="w-full max-w-md">
          <!-- Login Card -->
          <div class="bg-white rounded-2xl shadow-xl p-8">
            <div class="text-center mb-8">
              <div class="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <i data-lucide="shield-check" class="w-10 h-10 text-blue-600"></i>
              </div>
              <h2 class="text-3xl font-bold text-gray-900 mb-2">Welcome Back</h2>
              <p class="text-gray-600">Please sign in to access your dashboard</p>
            </div>
            
            <!-- Debug Info -->
            <div class="text-xs text-gray-400 text-center mb-6 bg-gray-50 rounded-lg p-2">
              Status: isAuthenticated = {{ isAuthenticated }}
            </div>
            
            <form @submit.prevent="login" class="space-y-6">
              <div>
                <label class="block text-sm font-semibold text-gray-700 mb-2">Username</label>
                <input 
                  v-model="loginForm.username" 
                  type="text" 
                  required
                  maxlength="50"
                  pattern="[a-zA-Z0-9_-]+"
                  autocomplete="username"
                  class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                  placeholder="Enter your username"
                >
              </div>
              <div>
                <label class="block text-sm font-semibold text-gray-700 mb-2">Password</label>
                <input 
                  v-model="loginForm.password" 
                  type="password" 
                  required
                  minlength="6"
                  maxlength="100"
                  autocomplete="current-password"
                  class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                  placeholder="Enter your password"
                >
              </div>
              
              <div v-if="loginError" class="bg-red-50 border border-red-200 text-red-600 text-sm p-3 rounded-xl text-center">
                {{ loginError }}
              </div>
              
              <div class="space-y-3">
                <button 
                  type="submit" 
                  :disabled="isLoggingIn"
                  class="w-full bg-blue-600 text-white py-3 px-4 rounded-xl hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all font-semibold"
                >
                  <span v-if="isLoggingIn">Authenticating...</span>
                  <span v-else>Sign In</span>
                </button>
                
                <!-- Debug/Skip Button -->
                <button 
                  type="button" 
                  @click="skipAuth"
                  class="w-full bg-gray-500 text-white py-2 px-4 rounded-xl hover:bg-gray-600 transition-all text-sm"
                >
                  Skip Authentication (Debug)
                </button>
              </div>
            </form>
            
            <!-- Credentials Info -->
            <div class="mt-8 p-4 bg-blue-50 rounded-xl border border-blue-200">
              <h3 class="text-sm font-semibold text-blue-900 mb-2">Demo Credentials</h3>
              <div class="text-sm text-blue-700 space-y-1">
                <div><span class="font-medium">Username:</span> admin</div>
                <div><span class="font-medium">Password:</span> iroa2024</div>
              </div>
            </div>
          </div>
        </div>
      </main>

      <!-- Footer -->
      <footer class="py-6 text-center text-gray-500 text-sm">
        <p>&copy; 2024 IROA - Intelligent Resource Optimization Agent</p>
      </footer>
    </div>

    <!-- Header -->
    <header v-if="isAuthenticated" class="gradient-bg text-white shadow-lg">
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
              <div :class="[
                'w-2 h-2 rounded-full',
                apiAvailable ? 'bg-green-400 animate-pulse' : 'bg-yellow-400'
              ]"></div>
              <span class="text-sm">{{ apiAvailable ? 'API Connected' : 'Mock Data Mode' }}</span>
            </div>
            <button @click="refreshData" class="bg-white bg-opacity-20 hover:bg-opacity-30 px-4 py-2 rounded-lg transition-all">
              <i data-lucide="refresh-cw" class="w-4 h-4"></i>
            </button>
            <button @click="logout" class="bg-red-500 bg-opacity-20 hover:bg-opacity-30 px-4 py-2 rounded-lg transition-all">
              <i data-lucide="log-out" class="w-4 h-4 mr-2"></i>
              Logout
            </button>
          </div>
        </div>
      </div>
    </header>

    <!-- Navigation -->
    <nav v-if="isAuthenticated" class="bg-white shadow-sm border-b">
      <div class="container mx-auto px-6">
        <nav class="flex space-x-1 bg-white rounded-lg p-1 shadow-sm">
          <button 
            v-for="tab in tabs" 
            :key="tab.id"
            @click="activeTab = tab.id"
            :class="[
              'px-4 py-2 rounded-md text-sm font-medium transition-all duration-200',
              activeTab === tab.id 
                ? 'bg-blue-500 text-white shadow-sm' 
                : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
            ]"
          >
            <i :class="tab.icon" class="mr-2"></i>
            {{ tab.name }}
          </button>
        </nav>
      </div>
    </nav>

    <!-- Main Content -->
    <main v-if="isAuthenticated" class="container mx-auto px-6 py-8">
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
            <div class="flex items-center space-x-3">
              <span class="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium">
                {{ recommendations.length }} Active
              </span>
              <button @click="refreshRecommendations" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-all flex items-center space-x-2">
                <i data-lucide="refresh-cw" class="w-4 h-4"></i>
                <span>Refresh</span>
              </button>
            </div>
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
      
      <!-- Administration Tab -->
      <div v-if="activeTab === 'admin'" class="container mx-auto px-6 py-8">
        <div class="mb-8">
          <h2 class="text-2xl font-bold text-gray-900 mb-2">System Administration</h2>
          <p class="text-gray-600">Manage integrations and monitor system health</p>
        </div>
        
        <!-- Integration Selection -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <div class="lg:col-span-1">
            <div class="bg-white rounded-xl shadow-sm p-6">
              <h3 class="text-lg font-semibold mb-4">Integration Type</h3>
              <div class="space-y-3">
                <div 
                  v-for="option in adminData.integrationOptions" 
                  :key="option.id"
                  @click="adminData.selectedIntegration = option.id"
                  :class="[
                    'p-4 rounded-lg border-2 cursor-pointer transition-all',
                    adminData.selectedIntegration === option.id 
                      ? 'border-blue-500 bg-blue-50' 
                      : 'border-gray-200 hover:border-gray-300'
                  ]"
                >
                  <div class="flex items-center space-x-3">
                    <span class="text-2xl">{{ option.icon }}</span>
                    <div>
                      <h4 class="font-medium text-gray-900">{{ option.name }}</h4>
                      <p class="text-sm text-gray-600">{{ option.description }}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div class="lg:col-span-2">
            <!-- Mac System Integration -->
            <div v-if="adminData.selectedIntegration === 'mac'" class="bg-white rounded-xl shadow-sm p-6">
              <h3 class="text-lg font-semibold mb-4">🍎 Mac System Integration</h3>
              <div class="space-y-6">
                <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <div class="flex items-center space-x-2 mb-2">
                    <i data-lucide="info" class="w-4 h-4 text-blue-600"></i>
                    <span class="text-sm font-medium text-blue-800">About Mac Monitoring</span>
                  </div>
                  <p class="text-sm text-blue-700">This integration monitors your Mac system resources and creates virtual VMs based on running processes for analysis.</p>
                </div>
                
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Monitoring Interval</label>
                    <select v-model="adminData.macMonitoring.interval" class="w-full border border-gray-300 rounded-md px-3 py-2">
                      <option value="10">10 seconds</option>
                      <option value="30">30 seconds</option>
                      <option value="60">1 minute</option>
                      <option value="300">5 minutes</option>
                    </select>
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Status</label>
                    <div class="flex items-center space-x-2">
                      <div :class="[
                        'w-3 h-3 rounded-full',
                        adminData.macMonitoring.isRunning ? 'bg-green-500' : 'bg-gray-400'
                      ]"></div>
                      <span class="text-sm text-gray-600">
                        {{ adminData.macMonitoring.isRunning ? 'Running' : 'Stopped' }}
                      </span>
                    </div>
                  </div>
                </div>
                
                <div class="flex space-x-3">
                  <button 
                    @click="startMacMonitoring"
                    :disabled="adminData.macMonitoring.isRunning"
                    class="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    🚀 Start Monitoring
                  </button>
                  <button 
                    @click="stopMacMonitoring"
                    :disabled="!adminData.macMonitoring.isRunning"
                    class="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    🛑 Stop Monitoring
                  </button>
                  <button 
                    @click="getMacStats"
                    class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                  >
                    📊 View Stats
                  </button>
                </div>
                
                <!-- Mac System Stats -->
                <div v-if="adminData.macMonitoring.currentStats" class="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div class="bg-gray-50 rounded-lg p-4">
                    <div class="flex items-center justify-between">
                      <span class="text-sm font-medium text-gray-600">CPU Usage</span>
                      <span class="text-lg font-bold text-gray-900">{{ adminData.macMonitoring.currentStats.cpu }}%</span>
                    </div>
                  </div>
                  <div class="bg-gray-50 rounded-lg p-4">
                    <div class="flex items-center justify-between">
                      <span class="text-sm font-medium text-gray-600">Memory Usage</span>
                      <span class="text-lg font-bold text-gray-900">{{ adminData.macMonitoring.currentStats.memory }}%</span>
                    </div>
                  </div>
                  <div class="bg-gray-50 rounded-lg p-4">
                    <div class="flex items-center justify-between">
                      <span class="text-sm font-medium text-gray-600">Disk Usage</span>
                      <span class="text-lg font-bold text-gray-900">{{ adminData.macMonitoring.currentStats.disk }}%</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- vCenter Integration -->
            <div v-if="adminData.selectedIntegration === 'vcenter'" class="bg-white rounded-xl shadow-sm p-6">
              <h3 class="text-lg font-semibold mb-4">🏢 VMware vCenter Integration</h3>
              <form @submit.prevent="testConnection('vcenter')" class="space-y-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">vCenter Host</label>
                  <input v-model="adminData.connectionForms.vcenter.host" type="text" class="w-full border border-gray-300 rounded-md px-3 py-2" placeholder="vcenter.local">
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Username</label>
                  <input v-model="adminData.connectionForms.vcenter.username" type="text" class="w-full border border-gray-300 rounded-md px-3 py-2" placeholder="administrator@vsphere.local" autocomplete="username">
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Password</label>
                  <input id="vcenter-password" v-model="adminData.connectionForms.vcenter.password" type="password" placeholder="Enter vCenter password" autocomplete="current-password" spellcheck="false" @input="debugCredentialInput('password', $event)" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                </div>
                <button type="submit" class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
                  Test Connection & Ingest
                </button>
              </form>
            </div>
            
            <!-- Zabbix Integration -->
            <div v-if="adminData.selectedIntegration === 'zabbix'" class="bg-white rounded-xl shadow-sm p-6">
              <h3 class="text-lg font-semibold mb-4">📊 Zabbix Integration</h3>
              <form @submit.prevent="testConnection('zabbix')" class="space-y-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Zabbix API URL</label>
                  <input v-model="adminData.connectionForms.zabbix.url" type="text" class="w-full border border-gray-300 rounded-md px-3 py-2" placeholder="http://your-zabbix-server/api_jsonrpc.php">
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Username</label>
                  <input v-model="adminData.connectionForms.zabbix.username" type="text" class="w-full border border-gray-300 rounded-md px-3 py-2" placeholder="Admin" autocomplete="username">
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Password</label>
                  <input id="zabbix-password" v-model="adminData.connectionForms.zabbix.password" type="password" placeholder="Enter Zabbix password" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500" autocomplete="current-password">
                </div>
                <button type="submit" class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
                  Test Connection & Ingest
                </button>
              </form>
            </div>
            
            <!-- Prometheus Integration -->
            <div v-if="adminData.selectedIntegration === 'prometheus'" class="bg-white rounded-xl shadow-sm p-6">
              <h3 class="text-lg font-semibold mb-4">🔥 Prometheus Integration</h3>
              <form @submit.prevent="testConnection('prometheus')" class="space-y-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Prometheus URL</label>
                  <input v-model="adminData.connectionForms.prometheus.url" type="text" class="w-full border border-gray-300 rounded-md px-3 py-2" placeholder="http://localhost:9090">
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Username (Optional)</label>
                  <input v-model="adminData.connectionForms.prometheus.username" type="text" class="w-full border border-gray-300 rounded-md px-3 py-2" placeholder="Leave empty if no authentication" autocomplete="username">
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Password (Optional)</label>
                  <input id="prometheus-password" v-model="adminData.connectionForms.prometheus.password" type="password" placeholder="Leave empty if no authentication" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500" autocomplete="current-password">
                </div>
                <button type="submit" class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
                  Test Connection & Ingest
                </button>
              </form>
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
      isAuthenticated: false,
      isLoggingIn: false,
      skipAuth: false,
      loginError: '',
      loginForm: {
        username: '',
        password: ''
      },
      sessionToken: null,
      apiBaseUrl: '',
      apiAvailable: false,
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
      // Admin panel data
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
          prometheus: { url: 'http://localhost:9090', username: '', password: '' }
        }
      }
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
    console.log('🚀 Vue app mounted')
    
    // Initialize API base URL
    this.apiBaseUrl = this.getApiBaseUrl()
    
    // Check authentication status
    await this.checkAuthStatus()
    
    // Initialize Lucide icons
    if (window.lucide) {
      window.lucide.createIcons()
    }
    
    // If already authenticated, initialize the app
    if (this.isAuthenticated) {
      await this.loadInfrastructure()
      this.initializeAuthenticatedApp()
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
    getApiBaseUrl() {
      // Check if we're running from file:// protocol
      if (window.location.protocol === 'file:') {
        return 'http://localhost:8001'
      }
      // For http/https, use relative path or same origin
      return window.location.origin.includes('localhost') 
        ? 'http://localhost:8001' 
        : `${window.location.protocol}//${window.location.hostname}:8001`
    },
    
    checkExistingSession() {
      const token = localStorage.getItem('iroa_session_token')
      const expiry = localStorage.getItem('iroa_session_expiry')
      
      console.log('🔍 Checking session - token:', !!token, 'expiry:', expiry)
      
      if (token && expiry && new Date().getTime() < parseInt(expiry)) {
        this.sessionToken = token
        this.isAuthenticated = true
        console.log('✅ Valid session found, setting isAuthenticated to true')
      } else {
        // Clean up expired session
        localStorage.removeItem('iroa_session_token')
        localStorage.removeItem('iroa_session_expiry')
        console.log('❌ No valid session found')
      }
    },

    async checkAuthStatus() {
      this.checkExistingSession()
      if (this.isAuthenticated) {
        await this.loadUserPermissions()
      }
    },

    async loadUserPermissions() {
      try {
        // Mock user permissions loading
        console.log('Loading user permissions...')
        // In a real app, this would load user roles/permissions from API
      } catch (error) {
        console.error('Error loading user permissions:', error)
      }
    },

    async loadInfrastructure() {
      try {
        console.log('Loading infrastructure data...')
        // This would load initial infrastructure data
        await this.checkApiConnection()
        await this.loadData()
      } catch (error) {
        console.error('Error loading infrastructure:', error)
      }
    },
    
    async login() {
      this.isLoggingIn = true
      this.loginError = ''
      
      try {
        // Input validation
        if (!this.loginForm.username || !this.loginForm.password) {
          this.loginError = 'Username and password are required'
        } else if (this.loginForm.username.length < 3 || this.loginForm.username.length > 50) {
          this.loginError = 'Username must be between 3 and 50 characters'
        } else if (this.loginForm.password.length < 6) {
          this.loginError = 'Password must be at least 6 characters'
        } else {
          // Sanitize input
          const username = this.loginForm.username.trim().toLowerCase()
          const password = this.loginForm.password
          
          // For demo purposes, using hardcoded credentials
          if (username === 'admin' && password === 'iroa2024') {
            // Generate session token
            const token = 'iroa_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9)
            const expiry = new Date().getTime() + (24 * 60 * 60 * 1000) // 24 hours
            
            // Store session
            localStorage.setItem('iroa_session_token', token)
            localStorage.setItem('iroa_session_expiry', expiry.toString())
            
            // Set authentication state
            this.sessionToken = token
            this.isAuthenticated = true
            
            console.log('✅ Login successful, isAuthenticated:', this.isAuthenticated)
            console.log('✅ Session token stored:', token)
            
            // Initialize app components after authentication
            this.initializeAuthenticatedApp()
          } else {
            this.loginError = 'Invalid username or password'
            await new Promise(resolve => setTimeout(resolve, 1000))
          }
        }
      } catch (error) {
        this.loginError = 'Authentication failed. Please try again.'
        console.error('Login error:', error)
      } finally {
        this.isLoggingIn = false
      }
    },
    
    logout() {
      // Clear session data
      localStorage.removeItem('iroa_session_token')
      localStorage.removeItem('iroa_session_expiry')
      
      this.isAuthenticated = false
      this.sessionToken = null
      this.loginForm.username = ''
      this.loginForm.password = ''
      this.loginError = ''
      
      // Clean up charts
      if (this.usageChart) {
        this.usageChart.destroy()
        this.usageChart = null
      }
      if (this.distributionChart) {
        this.distributionChart.destroy()
        this.distributionChart = null
      }
      if (this.forecastChart) {
        this.forecastChart.destroy()
        this.forecastChart = null
      }
    },
    
    async checkApiConnection() {
      try {
        // Validate the API URL first
        if (!this.apiBaseUrl || this.apiBaseUrl === '') {
          throw new Error('API base URL not configured')
        }
        
        const controller = new AbortController()
        const timeoutId = setTimeout(() => controller.abort(), 5000)
        
        const response = await fetch(`${this.apiBaseUrl}/health`, {
          method: 'GET',
          signal: controller.signal,
          headers: {
            'Authorization': `Bearer ${this.sessionToken}`,
            'Content-Type': 'application/json'
          }
        })
        
        clearTimeout(timeoutId)
        this.apiAvailable = response.ok
        if (this.apiAvailable) {
          console.log('✅ API server is available')
        }
      } catch (error) {
        this.apiAvailable = false
        console.warn('⚠️ API server unavailable, using mock data:', error.message)
      }
    },
    
    skipAuth() {
      console.log('🚨 Skipping authentication for debugging')
      
      // Generate a debug session token
      const token = 'debug_' + Date.now()
      const expiry = new Date().getTime() + (24 * 60 * 60 * 1000) // 24 hours
      
      // Store session
      localStorage.setItem('iroa_session_token', token)
      localStorage.setItem('iroa_session_expiry', expiry.toString())
      
      // Set authentication state
      this.sessionToken = token
      this.isAuthenticated = true
      
      console.log('🚨 Debug auth set - isAuthenticated:', this.isAuthenticated)
      
      // Initialize app components after authentication
      this.initializeAuthenticatedApp()
    },
    
    initializeAuthenticatedApp() {
      console.log('🔧 Initializing authenticated app components')
      
      // Use nextTick to ensure DOM is updated after authentication state change
      this.$nextTick(async () => {
        try {
          // Initialize Lucide icons first
          if (window.lucide) {
            window.lucide.createIcons()
          }
          
          // Check API connection and load data
          await this.checkApiConnection()
          await this.loadData()
          
          // Initialize charts after data is loaded
          this.$nextTick(() => {
            this.initializeCharts()
          })
          
          console.log('✅ App initialization complete')
        } catch (error) {
          console.error('Error initializing authenticated app:', error)
          // Don't reset authentication on initialization error
        }
      })
    },
    
    async loadData() {
      this.loading = true
      try {
        if (this.apiAvailable) {
          // Load recommendations from API
          const recRes = await fetch(`${this.apiBaseUrl}/recommendations`, {
            headers: {
              'Authorization': `Bearer ${this.sessionToken}`,
              'Content-Type': 'application/json'
            }
          })
          if (recRes.ok) {
            this.recommendations = await recRes.json()
          } else {
            console.warn('Failed to load recommendations:', recRes.status)
            this.recommendations = this.getMockRecommendations()
          }
          
          // Load underutilized VMs from API
          const underRes = await fetch(`${this.apiBaseUrl}/underutilized`, {
            headers: {
              'Authorization': `Bearer ${this.sessionToken}`,
              'Content-Type': 'application/json'
            }
          })
          if (underRes.ok) {
            this.underutilizedVMs = await underRes.json()
            // Update stats
            this.stats[1].value = this.underutilizedVMs.length.toString()
          } else {
            console.warn('Failed to load underutilized VMs:', underRes.status)
            this.underutilizedVMs = this.getMockUnderutilizedVMs()
            this.stats[1].value = this.underutilizedVMs.length.toString()
          }
        } else {
          // Use mock data when API is unavailable
          this.recommendations = this.getMockRecommendations()
          this.underutilizedVMs = this.getMockUnderutilizedVMs()
          this.stats[1].value = this.underutilizedVMs.length.toString()
        }
      } catch (error) {
        console.error('Error loading data:', error)
        // Set mock data on error
        this.recommendations = this.getMockRecommendations()
        this.underutilizedVMs = this.getMockUnderutilizedVMs()
        this.stats[1].value = this.underutilizedVMs.length.toString()
      } finally {
        this.loading = false
      }
    },
    getMockRecommendations() {
      return [
        {
          vm: 'test-vm-01',
          reason: 'underutilized',
          suggestion: 'Consider reducing CPU allocation or consolidating workload',
          details: { avg_cpu: 5, avg_mem: 17 }
        },
        {
          vm: 'backup-vm-01',
          reason: 'underutilized',
          suggestion: 'Schedule-based scaling could optimize resource usage',
          details: { avg_cpu: 5, avg_mem: 17 }
        }
      ]
    },
    
    getMockUnderutilizedVMs() {
      return this.mockVMs.filter(vm => vm.cpu < 10 && vm.memory_usage < 20)
    },
    
    async refreshData() {
      await this.checkApiConnection()
      await this.loadData()
      this.initializeCharts()
    },
    async refreshRecommendations() {
      this.loading = true
      try {
        if (this.apiAvailable) {
          // Load recommendations from API
          const recRes = await fetch(`${this.apiBaseUrl}/recommendations`, {
            headers: {
              'Authorization': `Bearer ${this.sessionToken}`,
              'Content-Type': 'application/json'
            }
          })
          if (recRes.ok) {
            this.recommendations = await recRes.json()
          } else {
            console.warn('Failed to load recommendations:', recRes.status)
            this.recommendations = this.getMockRecommendations()
          }
        } else {
          // Use mock data when API is unavailable
          this.recommendations = this.getMockRecommendations()
        }
      } catch (error) {
        console.error('Error refreshing recommendations:', error)
        this.recommendations = this.getMockRecommendations()
      } finally {
        this.loading = false
      }
    },
    async getVMForecast(vmId) {
      try {
        if (this.apiAvailable) {
          const res = await fetch(`${this.apiBaseUrl}/forecast/${vmId}`, {
            headers: {
              'Authorization': `Bearer ${this.sessionToken}`,
              'Content-Type': 'application/json'
            }
          })
          if (res.ok) {
            const data = await res.json()
            this.forecast = data.cpu_forecast || []
          } else {
            console.warn('Failed to load forecast:', res.status)
            this.forecast = this.getMockForecast()
          }
        } else {
          this.forecast = this.getMockForecast()
        }
        
        this.selectedVM = this.mockVMs.find(vm => vm.id === vmId)
        this.activeTab = 'analytics'
        
        // Update forecast chart
        this.$nextTick(() => {
          this.initializeForecastChart()
        })
      } catch (error) {
        console.error('Error loading forecast:', error)
        this.forecast = this.getMockForecast()
        this.selectedVM = this.mockVMs.find(vm => vm.id === vmId)
        this.activeTab = 'analytics'
        this.$nextTick(() => {
          this.initializeForecastChart()
        })
      }
    },
    getMockForecast() {
      // Generate mock 24-hour forecast data
      return Array.from({ length: 24 }, (_, i) => {
        return Math.round(30 + Math.sin(i * 0.3) * 20 + Math.random() * 10)
      })
    },
    
    async getAnomalies(vmId) {
      try {
        if (this.apiAvailable) {
          const res = await fetch(`${this.apiBaseUrl}/anomalies/${vmId}`, {
            headers: {
              'Authorization': `Bearer ${this.sessionToken}`,
              'Content-Type': 'application/json'
            }
          })
          if (res.ok) {
            const data = await res.json()
            this.anomalies = data.anomalies || []
          } else {
            this.anomalies = []
          }
        } else {
          this.anomalies = []
        }
      } catch (error) {
        console.error('Error loading anomalies:', error)
        this.anomalies = []
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
    },
    
    // Admin panel methods
    async startMacMonitoring() {
      try {
        if (!this.apiAvailable) {
          alert('⚠️ API server is not available. This feature requires the backend server.')
          return
        }
        
        const response = await fetch(`${this.apiBaseUrl}/admin/mac/start`, {
          method: 'POST',
          headers: { 
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${this.sessionToken}`
          },
          body: JSON.stringify({ interval: this.adminData.macMonitoring.interval })
        })
        
        if (response.ok) {
          const result = await response.json()
          this.adminData.macMonitoring.isRunning = true
          this.adminData.macMonitoring.lastUpdate = new Date().toISOString()
          console.log('Mac monitoring started:', result)
          
          // Refresh data to show new VMs
          await this.loadData()
        } else {
          console.error('Failed to start Mac monitoring')
        }
      } catch (error) {
        console.error('Error starting Mac monitoring:', error)
      }
    },
    
    async stopMacMonitoring() {
      try {
        if (!this.apiAvailable) {
          alert('⚠️ API server is not available. This feature requires the backend server.')
          return
        }
        
        const response = await fetch(`${this.apiBaseUrl}/admin/mac/stop`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${this.sessionToken}`
          }
        })
        
        if (response.ok) {
          this.adminData.macMonitoring.isRunning = false
          console.log('Mac monitoring stopped')
        } else {
          console.error('Failed to stop Mac monitoring')
        }
      } catch (error) {
        console.error('Error stopping Mac monitoring:', error)
      }
    },
    
    async getMacStats() {
      try {
        if (!this.apiAvailable) {
          alert('⚠️ API server is not available. This feature requires the backend server.')
          return
        }
        
        const response = await fetch(`${this.apiBaseUrl}/admin/mac/stats`, {
          headers: {
            'Authorization': `Bearer ${this.sessionToken}`
          }
        })
        
        if (response.ok) {
          const stats = await response.json()
          this.adminData.macMonitoring.currentStats = {
            cpu: stats.cpu_usage.toFixed(1),
            memory: stats.memory_usage.toFixed(1),
            disk: stats.disk_usage.toFixed(1)
          }
          this.adminData.macMonitoring.systemInfo = stats.system_info
        } else {
          console.error('Failed to get Mac stats')
        }
      } catch (error) {
        console.error('Error getting Mac stats:', error)
      }
    },
    
    debugCredentialInput(field, event) {
      console.log(`Debug: ${field} field updated`, event.target.value ? '[REDACTED]' : 'empty')
    },
    
    async testConnection(type) {
      try {
        if (!this.apiAvailable) {
          alert('⚠️ API server is not available. This feature requires the backend server.')
          return
        }
        
        const formData = this.adminData.connectionForms[type]
        const response = await fetch(`${this.apiBaseUrl}/admin/${type}/test`, {
          method: 'POST',
          headers: { 
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${this.sessionToken}`
          },
          body: JSON.stringify(formData)
        })
        
        if (response.ok) {
          const result = await response.json()
          console.log(`${type} connection successful:`, result)
          alert(`✅ ${type} integration successful!`)
        } else {
          const error = await response.text()
          console.error(`${type} connection failed:`, error)
          alert(`❌ Failed to connect to ${type}: ${error}`)
        }
      } catch (error) {
        console.error(`Error testing ${type} connection:`, error)
        alert(`❌ Error testing ${type} connection: ${error.message}`)
      }
    }
  }
}
</script>
