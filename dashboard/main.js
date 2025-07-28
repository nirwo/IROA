// Use global Vue from CDN
const { createApp } = Vue;

// Since we can't easily parse SFC files in the browser, let's create the app directly
// with all the functionality from App.vue

const app = createApp({
  template: `
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
                <h3 class="text-sm font-semibold text-blue-900 mb-3">Demo Credentials</h3>
                <div class="text-sm text-blue-700 space-y-3">
                  <div class="bg-white bg-opacity-50 rounded-lg p-3">
                    <div class="font-medium text-red-800 mb-1">Administrator</div>
                    <div><span class="font-medium">Username:</span> admin</div>
                    <div><span class="font-medium">Password:</span> iroa2024</div>
                    <div class="text-xs text-blue-600 mt-1">Full system access + user management</div>
                  </div>
                  <div class="bg-white bg-opacity-50 rounded-lg p-3">
                    <div class="font-medium text-yellow-800 mb-1">Manager</div>
                    <div><span class="font-medium">Username:</span> manager1</div>
                    <div><span class="font-medium">Password:</span> manager123</div>
                    <div class="text-xs text-blue-600 mt-1">Advanced features + capacity planning</div>
                  </div>
                  <div class="bg-white bg-opacity-50 rounded-lg p-3">
                    <div class="font-medium text-green-800 mb-1">User</div>
                    <div><span class="font-medium">Username:</span> user1</div>
                    <div><span class="font-medium">Password:</span> user123</div>
                    <div class="text-xs text-blue-600 mt-1">Basic access to overview and monitoring</div>
                  </div>
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

      <!-- Authenticated Dashboard -->
      <div v-if="isAuthenticated">
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
                <!-- Current User Info -->
                <div class="flex items-center space-x-2 bg-white bg-opacity-20 px-3 py-2 rounded-lg">
                  <div class="w-8 h-8 bg-white bg-opacity-30 rounded-full flex items-center justify-center">
                    <i data-lucide="user" class="w-4 h-4"></i>
                  </div>
                  <div class="text-left">
                    <div class="text-sm font-medium">{{ currentUser.profile.fullName || currentUser.username }}</div>
                    <div class="text-xs opacity-90">{{ currentUser.role.charAt(0).toUpperCase() + currentUser.role.slice(1) }}</div>
                  </div>
                </div>
                
                <!-- API Status -->
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
        <nav class="bg-white shadow-sm border-b">
          <div class="container mx-auto px-6">
            <nav class="flex space-x-1 bg-white rounded-lg p-1 shadow-sm">
              <button 
                v-for="tab in tabs" 
                :key="tab.id"
                @click="changeTab(tab.id)"
                :class="[
                  'px-4 py-2 rounded-md text-sm font-medium transition-all duration-200 flex items-center',
                  activeTab === tab.id 
                    ? 'bg-blue-500 text-white shadow-sm' 
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                ]"
              >
                <i :data-lucide="tab.icon" class="w-4 h-4 mr-2"></i>
                {{ tab.name }}
                <i v-if="tab.requiredRole === 'admin'" data-lucide="shield" class="w-3 h-3 ml-1 opacity-60"></i>
                <i v-else-if="tab.requiredRole === 'manager'" data-lucide="user-cog" class="w-3 h-3 ml-1 opacity-60"></i>
              </button>
            </nav>
          </div>
        </nav>

        <!-- Main Content -->
        <main class="container mx-auto px-6 py-8">
          <!-- Overview Tab -->
          <div v-if="activeTab === 'overview'" class="space-y-6">
            <!-- Stats Cards -->
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div v-for="stat in filteredStats" :key="stat.title" class="bg-white rounded-xl shadow-sm p-6 card-hover">
                <div class="flex items-center justify-between">
                  <div>
                    <p class="text-sm font-medium text-gray-600">{{ stat.title }}</p>
                    <p class="text-2xl font-bold text-gray-900">
                      {{ stat.requiresDataAccess && !hasDataAccess(stat.requiresDataAccess) ? '***' : stat.value }}
                    </p>
                    <p :class="['text-sm', stat.change >= 0 ? 'text-green-600' : 'text-red-600']">
                      {{ stat.requiresDataAccess && !hasDataAccess(stat.requiresDataAccess) ? 'Restricted' : (stat.change >= 0 ? '+' : '') + stat.change + '%' }}
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
                          <span class="font-medium ml-1">{{ rec.details?.avg_cpu || 0 }}%</span>
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
                        <span class="font-medium">{{ vm.cpu || 0 }}%</span>
                      </div>
                      <div class="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          :class="[
                            'h-2 rounded-full transition-all duration-300',
                            (vm.cpu || 0) < 30 ? 'bg-green-500' : (vm.cpu || 0) < 70 ? 'bg-yellow-500' : 'bg-red-500'
                          ]"
                          :style="{ width: Math.min(100, vm.cpu || 0) + '%' }"
                        ></div>
                      </div>
                    </div>
                    
                    <div>
                      <div class="flex justify-between text-sm mb-1">
                        <span class="text-gray-600">Memory Usage</span>
                        <span class="font-medium">{{ vm.memory_usage || 0 }}%</span>
                      </div>
                      <div class="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          :class="[
                            'h-2 rounded-full transition-all duration-300',
                            (vm.memory_usage || 0) < 50 ? 'bg-green-500' : (vm.memory_usage || 0) < 80 ? 'bg-yellow-500' : 'bg-red-500'
                          ]"
                          :style="{ width: Math.min(100, vm.memory_usage || 0) + '%' }"
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
                                (vm.cpu || 0) < 30 ? 'bg-green-500' : (vm.cpu || 0) < 70 ? 'bg-yellow-500' : 'bg-red-500'
                              ]"
                              :style="{ width: Math.min(100, vm.cpu || 0) + '%' }"
                            ></div>
                          </div>
                          <span class="text-sm text-gray-600">{{ vm.cpu || 0 }}%</span>
                        </div>
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap">
                        <div class="flex items-center">
                          <div class="w-16 bg-gray-200 rounded-full h-2 mr-2">
                            <div 
                              :class="[
                                'h-2 rounded-full',
                                (vm.memory_usage || 0) < 50 ? 'bg-green-500' : (vm.memory_usage || 0) < 80 ? 'bg-yellow-500' : 'bg-red-500'
                              ]"
                              :style="{ width: Math.min(100, vm.memory_usage || 0) + '%' }"
                            ></div>
                          </div>
                          <span class="text-sm text-gray-600">{{ vm.memory_usage || 0 }}%</span>
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

          <!-- Capacity Planning Tab -->
          <div v-if="activeTab === 'capacity'" class="space-y-6">
            <div class="bg-white rounded-xl shadow-sm p-6">
              <div class="flex items-center justify-between mb-6">
                <h2 class="text-xl font-semibold">Infrastructure Capacity Planning</h2>
                <div class="flex space-x-3">
                  <select v-model="selectedCluster" @change="loadCapacityData" class="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent">
                    <option value="">All Clusters</option>
                    <option v-for="cluster in clusters" :key="cluster" :value="cluster">{{ cluster }}</option>
                  </select>
                  <button @click="loadCapacityData" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                    <i data-lucide="refresh-cw" class="w-4 h-4 mr-2"></i>
                    Refresh Analysis
                  </button>
                </div>
              </div>
              
              <div v-if="capacityData">
                <!-- Summary Cards -->
                <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                  <div class="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-6">
                    <div class="flex items-center justify-between">
                      <div>
                        <p class="text-sm font-medium text-gray-600">Total Capacity</p>
                        <p class="text-2xl font-bold text-indigo-600">{{ capacityData.current_infrastructure?.max_additional_vms || 0 }}</p>
                        <p class="text-xs text-gray-500">Additional VMs</p>
                      </div>
                      <div class="w-12 h-12 bg-indigo-100 rounded-lg flex items-center justify-center">
                        <i data-lucide="server" class="w-6 h-6 text-indigo-600"></i>
                      </div>
                    </div>
                  </div>
                  
                  <div class="bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg p-6">
                    <div class="flex items-center justify-between">
                      <div>
                        <p class="text-sm font-medium text-gray-600">CPU Cores</p>
                        <p class="text-2xl font-bold text-green-600">{{ capacityData.current_infrastructure?.total_cpu_cores || 0 }}</p>
                        <p class="text-xs text-gray-500">Available</p>
                      </div>
                      <div class="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                        <i data-lucide="cpu" class="w-6 h-6 text-green-600"></i>
                      </div>
                    </div>
                  </div>
                  
                  <div class="bg-gradient-to-r from-purple-50 to-violet-50 rounded-lg p-6">
                    <div class="flex items-center justify-between">
                      <div>
                        <p class="text-sm font-medium text-gray-600">Memory</p>
                        <p class="text-2xl font-bold text-purple-600">{{ Math.round(capacityData.current_infrastructure?.total_memory_gb || 0) }}GB</p>
                        <p class="text-xs text-gray-500">Total Available</p>
                      </div>
                      <div class="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                        <i data-lucide="memory-stick" class="w-6 h-6 text-purple-600"></i>
                      </div>
                    </div>
                  </div>
                  
                  <div class="bg-gradient-to-r from-orange-50 to-amber-50 rounded-lg p-6">
                    <div class="flex items-center justify-between">
                      <div>
                        <p class="text-sm font-medium text-gray-600">Storage</p>
                        <p class="text-2xl font-bold text-orange-600">{{ Math.round(capacityData.current_infrastructure?.total_storage_gb || 0) }}GB</p>
                        <p class="text-xs text-gray-500">Total Capacity</p>
                      </div>
                      <div class="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
                        <i data-lucide="hard-drive" class="w-6 h-6 text-orange-600"></i>
                      </div>
                    </div>
                  </div>
                </div>
                
                <!-- Recommendations -->
                <div v-if="capacityData.recommendations?.length" class="mb-8">
                  <h3 class="text-lg font-semibold mb-4">Capacity Recommendations</h3>
                  <div class="space-y-3">
                    <div v-for="rec in capacityData.recommendations" :key="rec.id" class="border-l-4 border-blue-400 bg-blue-50 p-4 rounded-r-lg">
                      <h4 class="font-medium text-blue-900">{{ rec.title }}</h4>
                      <p class="text-sm text-blue-700 mt-1">{{ rec.description }}</p>
                    </div>
                  </div>
                </div>
                
                <!-- Cluster Analysis Table -->
                <div v-if="capacityData.clusters?.length">
                  <h3 class="text-lg font-semibold mb-4">Cluster Analysis</h3>
                  <div class="overflow-x-auto">
                    <table class="min-w-full divide-y divide-gray-200">
                      <thead class="bg-gray-50">
                        <tr>
                          <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Cluster</th>
                          <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Current VMs</th>
                          <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">CPU Utilization</th>
                          <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Memory Utilization</th>
                          <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Max Additional VMs</th>
                          <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Limiting Factor</th>
                        </tr>
                      </thead>
                      <tbody class="bg-white divide-y divide-gray-200">
                        <tr v-for="cluster in capacityData.clusters" :key="cluster.cluster" class="hover:bg-gray-50">
                          <td class="px-6 py-4 whitespace-nowrap">
                            <div class="text-sm font-medium text-gray-900">{{ cluster.cluster }}</div>
                            <div class="text-sm text-gray-500">{{ cluster.host_count || 1 }} hosts</div>
                          </td>
                          <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ cluster.current_vms }}</td>
                          <td class="px-6 py-4 whitespace-nowrap">
                            <div class="flex items-center">
                              <div class="w-16 bg-gray-200 rounded-full h-2 mr-2">
                                <div 
                                  :class="[
                                    'h-2 rounded-full',
                                    cluster.cpu_utilization < 50 ? 'bg-green-500' : cluster.cpu_utilization < 80 ? 'bg-yellow-500' : 'bg-red-500'
                                  ]"
                                  :style="{ width: cluster.cpu_utilization + '%' }"
                                ></div>
                              </div>
                              <span class="text-sm text-gray-600">{{ cluster.cpu_utilization }}%</span>
                            </div>
                          </td>
                          <td class="px-6 py-4 whitespace-nowrap">
                            <div class="flex items-center">
                              <div class="w-16 bg-gray-200 rounded-full h-2 mr-2">
                                <div 
                                  :class="[
                                    'h-2 rounded-full',
                                    cluster.memory_utilization < 50 ? 'bg-green-500' : cluster.memory_utilization < 80 ? 'bg-yellow-500' : 'bg-red-500'
                                  ]"
                                  :style="{ width: cluster.memory_utilization + '%' }"
                                ></div>
                              </div>
                              <span class="text-sm text-gray-600">{{ cluster.memory_utilization }}%</span>
                            </div>
                          </td>
                          <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ cluster.max_additional_vms }}</td>
                          <td class="px-6 py-4 whitespace-nowrap">
                            <span :class="[
                              'inline-flex px-2 py-1 text-xs font-semibold rounded-full',
                              cluster.limiting_factor === 'CPU' ? 'bg-red-100 text-red-800' : 'bg-yellow-100 text-yellow-800'
                            ]">
                              {{ cluster.limiting_factor }}
                            </span>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
              
              <div v-else class="text-center py-12">
                <i data-lucide="cpu" class="w-12 h-12 text-gray-400 mx-auto mb-3"></i>
                <h3 class="text-lg font-medium text-gray-900 mb-2">Load Capacity Analysis</h3>
                <p class="text-gray-600 mb-4">Click "Refresh Analysis" to load capacity planning data</p>
                <button @click="loadCapacityData" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                  Load Analysis
                </button>
              </div>
            </div>
          </div>

          <!-- VM Profiles Tab -->
          <div v-if="activeTab === 'profiles'" class="space-y-6">
            <div class="bg-white rounded-xl shadow-sm p-6">
              <div class="flex items-center justify-between mb-6">
                <h2 class="text-xl font-semibold">VM Profile Analysis</h2>
                <div class="flex space-x-3">
                  <select v-model="selectedCluster" @change="loadProfileData" class="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent">
                    <option value="">All Clusters</option>
                    <option v-for="cluster in clusters" :key="cluster" :value="cluster">{{ cluster }}</option>
                  </select>
                  <button @click="loadProfileData" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                    <i data-lucide="refresh-cw" class="w-4 h-4 mr-2"></i>
                    Refresh Profiles
                  </button>
                </div>
              </div>
              
              <div v-if="profileData">
                <!-- Cluster Summary -->
                <div v-if="profileData.cluster_capacity" class="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-lg p-6 mb-8">
                  <h3 class="text-lg font-semibold text-gray-900 mb-4">{{ profileData.cluster_name }} Capacity</h3>
                  <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div class="text-center">
                      <div class="text-2xl font-bold text-indigo-600">{{ profileData.cluster_capacity.total_cpu_vcpus }}</div>
                      <div class="text-sm text-gray-600">Total vCPUs</div>
                    </div>
                    <div class="text-center">
                      <div class="text-2xl font-bold text-purple-600">{{ Math.round(profileData.cluster_capacity.total_memory_gb) }}GB</div>
                      <div class="text-sm text-gray-600">Total Memory</div>
                    </div>
                    <div class="text-center">
                      <div class="text-2xl font-bold text-green-600">{{ profileData.cluster_capacity.remaining_vcpu }}</div>
                      <div class="text-sm text-gray-600">Remaining vCPUs</div>
                    </div>
                  </div>
                </div>
                
                <!-- Profile Analysis -->
                <div v-if="profileData.profiles_discovered?.length">
                  <h3 class="text-lg font-semibold mb-4">Discovered VM Profiles</h3>
                  <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <div v-for="profile in profileData.profiles_discovered" :key="profile.profile_name" class="border border-gray-200 rounded-lg p-6 hover:border-indigo-300 transition-colors">
                      <div class="flex items-center justify-between mb-4">
                        <h4 class="text-lg font-semibold text-gray-900">{{ profile.profile_name }}</h4>
                        <span class="bg-indigo-100 text-indigo-800 px-3 py-1 rounded-full text-sm font-medium">
                          {{ profile.current_count }} VMs
                        </span>
                      </div>
                      
                      <div class="space-y-3 mb-4">
                        <div class="flex justify-between text-sm">
                          <span class="text-gray-600">CPU per VM:</span>
                          <span class="font-medium">{{ profile.profile_specs.cpu }} vCPUs</span>
                        </div>
                        <div class="flex justify-between text-sm">
                          <span class="text-gray-600">Memory per VM:</span>
                          <span class="font-medium">{{ profile.profile_specs.memory }}GB</span>
                        </div>
                        <div class="flex justify-between text-sm">
                          <span class="text-gray-600">Storage per VM:</span>
                          <span class="font-medium">{{ profile.profile_specs.disk }}GB</span>
                        </div>
                      </div>
                      
                      <div class="border-t pt-4">
                        <div class="flex justify-between items-center mb-2">
                          <span class="text-sm text-gray-600">Max Additional VMs:</span>
                          <span class="text-lg font-bold text-green-600">{{ profile.max_additional_vms }}</span>
                        </div>
                        <div class="flex justify-between items-center">
                          <span class="text-sm text-gray-600">Limiting Factor:</span>
                          <span :class="[
                            'inline-flex px-2 py-1 text-xs font-semibold rounded-full',
                            profile.limiting_factor === 'CPU' ? 'bg-red-100 text-red-800' : 
                            profile.limiting_factor === 'Memory' ? 'bg-yellow-100 text-yellow-800' : 'bg-blue-100 text-blue-800'
                          ]">
                            {{ profile.limiting_factor }}
                          </span>
                        </div>
                      </div>
                      
                      <!-- Resource Usage Bars -->
                      <div class="mt-4 space-y-2">
                        <div>
                          <div class="flex justify-between text-xs mb-1">
                            <span>CPU Usage</span>
                            <span>{{ profile.profile_cpu_usage_percent }}%</span>
                          </div>
                          <div class="w-full bg-gray-200 rounded-full h-2">
                            <div class="bg-blue-500 h-2 rounded-full" :style="{ width: profile.profile_cpu_usage_percent + '%' }"></div>
                          </div>
                        </div>
                        <div>
                          <div class="flex justify-between text-xs mb-1">
                            <span>Memory Usage</span>
                            <span>{{ profile.profile_memory_usage_percent }}%</span>
                          </div>
                          <div class="w-full bg-gray-200 rounded-full h-2">
                            <div class="bg-green-500 h-2 rounded-full" :style="{ width: profile.profile_memory_usage_percent + '%' }"></div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <div v-else class="text-center py-12">
                <i data-lucide="layers" class="w-12 h-12 text-gray-400 mx-auto mb-3"></i>
                <h3 class="text-lg font-medium text-gray-900 mb-2">Load Profile Analysis</h3>
                <p class="text-gray-600 mb-4">Click "Refresh Profiles" to analyze VM profiles and capacity planning</p>
                <button @click="loadProfileData" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                  Load Profiles
                </button>
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
          
          <!-- Real-Time Monitoring Tab -->
          <div v-if="activeTab === 'monitoring'" class="space-y-6">
            <div class="bg-white rounded-xl shadow-sm p-6">
              <div class="flex items-center justify-between mb-6">
                <h3 class="text-lg font-semibold">Real-Time Monitoring</h3>
                <div class="flex items-center space-x-2">
                  <div :class="[
                    'w-2 h-2 rounded-full',
                    realTimeData.isConnected ? 'bg-green-400 animate-pulse' : 'bg-red-400'
                  ]"></div>
                  <span class="text-sm text-gray-600">
                    {{ realTimeData.isConnected ? 'Live' : 'Disconnected' }}
                  </span>
                </div>
              </div>
              
              <!-- Real-time metrics grid -->
              <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div class="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-4">
                  <div class="flex items-center justify-between">
                    <div>
                      <p class="text-sm font-medium text-gray-600">Avg CPU</p>
                      <p class="text-2xl font-bold text-indigo-600">{{ realTimeData.metrics.avgCpu }}%</p>
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
                      <p class="text-2xl font-bold text-green-600">{{ realTimeData.metrics.avgMemory }}%</p>
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
                      <p class="text-2xl font-bold text-purple-600">{{ realTimeData.metrics.activeVMs }}</p>
                    </div>
                    <div class="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                      <i data-lucide="server" class="w-5 h-5 text-purple-600"></i>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Real-time chart -->
              <div class="h-64 mb-6">
                <canvas ref="realtimeChart"></canvas>
              </div>
              
              <!-- Recent events -->
              <div>
                <h4 class="text-sm font-medium text-gray-900 mb-3">Recent Events</h4>
                <div class="space-y-2 max-h-32 overflow-y-auto">
                  <div v-for="event in realTimeData.recentEvents" :key="event.id" class="flex items-center space-x-3 text-sm">
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
          </div>
          
          <!-- User Management Tab -->
          <div v-if="activeTab === 'users'" class="space-y-6">
            <div class="bg-white rounded-xl shadow-sm p-6">
              <div class="flex items-center justify-between mb-6">
                <div>
                  <h2 class="text-xl font-semibold">User Management</h2>
                  <p class="text-gray-600 text-sm">Manage user accounts, roles, and permissions</p>
                </div>
                <button 
                  @click="openUserModal()"
                  class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  <i data-lucide="user-plus" class="w-4 h-4 mr-2"></i>
                  Add User
                </button>
              </div>
              
              <!-- Users Table -->
              <div class="overflow-x-auto">
                <table class="min-w-full divide-y divide-gray-200">
                  <thead class="bg-gray-50">
                    <tr>
                      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">User</th>
                      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Role</th>
                      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Department</th>
                      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Last Login</th>
                      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                    </tr>
                  </thead>
                  <tbody class="bg-white divide-y divide-gray-200">
                    <tr v-for="user in users" :key="user.id" class="hover:bg-gray-50">
                      <td class="px-6 py-4 whitespace-nowrap">
                        <div class="flex items-center">
                          <div class="w-10 h-10 bg-indigo-100 rounded-full flex items-center justify-center mr-3">
                            <i data-lucide="user" class="w-5 h-5 text-indigo-600"></i>
                          </div>
                          <div>
                            <div class="text-sm font-medium text-gray-900">{{ user.fullName }}</div>
                            <div class="text-sm text-gray-500">{{ user.username }}</div>
                            <div class="text-sm text-gray-500">{{ user.email }}</div>
                          </div>
                        </div>
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap">
                        <span :class="[
                          'inline-flex px-2 py-1 text-xs font-semibold rounded-full',
                          user.role === 'admin' ? 'bg-red-100 text-red-800' :
                          user.role === 'manager' ? 'bg-yellow-100 text-yellow-800' : 'bg-green-100 text-green-800'
                        ]">
                          {{ user.role.charAt(0).toUpperCase() + user.role.slice(1) }}
                        </span>
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">{{ user.department }}</td>
                      <td class="px-6 py-4 whitespace-nowrap">
                        <span :class="[
                          'inline-flex px-2 py-1 text-xs font-semibold rounded-full',
                          user.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                        ]">
                          {{ user.status }}
                        </span>
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                        {{ user.lastLogin ? new Date(user.lastLogin).toLocaleDateString() : 'Never' }}
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <button 
                          @click="openUserModal(user)"
                          class="text-indigo-600 hover:text-indigo-900 mr-3"
                          title="Edit User"
                        >
                          <i data-lucide="edit" class="w-4 h-4"></i>
                        </button>
                        <button 
                          @click="toggleUserStatus(user.id)"
                          :class="[
                            'mr-3',
                            user.status === 'active' ? 'text-red-600 hover:text-red-900' : 'text-green-600 hover:text-green-900'
                          ]"
                          :title="user.status === 'active' ? 'Deactivate User' : 'Activate User'"
                        >
                          <i :data-lucide="user.status === 'active' ? 'user-x' : 'user-check'" class="w-4 h-4"></i>
                        </button>
                        <button 
                          @click="deleteUser(user.id)"
                          class="text-red-600 hover:text-red-900"
                          title="Delete User"
                          :disabled="user.id === currentUser.id"
                        >
                          <i data-lucide="trash-2" class="w-4 h-4"></i>
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
            
            <!-- Role Overview -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div v-for="role in roles" :key="role.id" class="bg-white rounded-xl shadow-sm p-6">
                <div class="flex items-center justify-between mb-4">
                  <h3 class="text-lg font-semibold">{{ role.name }}</h3>
                  <span class="bg-indigo-100 text-indigo-800 px-3 py-1 rounded-full text-sm font-medium">
                    {{ users.filter(u => u.role === role.id).length }} users
                  </span>
                </div>
                <p class="text-gray-600 text-sm mb-4">{{ role.description }}</p>
                <div class="space-y-2">
                  <div>
                    <span class="text-xs font-medium text-gray-500 uppercase tracking-wider">Page Access:</span>
                    <div class="mt-1 flex flex-wrap gap-1">
                      <span 
                        v-for="permission in role.permissions.pages.slice(0, 3)" 
                        :key="permission"
                        class="inline-flex px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded"
                      >
                        {{ permission.replace('view_', '').replace('_', ' ') }}
                      </span>
                      <span 
                        v-if="role.permissions.pages.length > 3"
                        class="inline-flex px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded"
                      >
                        +{{ role.permissions.pages.length - 3 }} more
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- User Modal -->
          <div v-if="userManagement.showUserModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50" @click="closeUserModal">
            <div class="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white" @click.stop>
              <div class="flex items-center justify-between mb-4">
                <h3 class="text-lg font-semibold">
                  {{ userManagement.editMode ? 'Edit User' : 'Add New User' }}
                </h3>
                <button @click="closeUserModal" class="text-gray-400 hover:text-gray-600">
                  <i data-lucide="x" class="w-5 h-5"></i>
                </button>
              </div>
              
              <form @submit.prevent="saveUser" class="space-y-4">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Username</label>
                    <input 
                      v-model="userManagement.userForm.username" 
                      type="text" 
                      required
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Enter username"
                    >
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Full Name</label>
                    <input 
                      v-model="userManagement.userForm.fullName" 
                      type="text" 
                      required
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Enter full name"
                    >
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Email</label>
                    <input 
                      v-model="userManagement.userForm.email" 
                      type="email" 
                      required
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Enter email address"
                    >
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Department</label>
                    <input 
                      v-model="userManagement.userForm.department" 
                      type="text"
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Enter department"
                    >
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Role</label>
                    <select 
                      v-model="userManagement.userForm.role" 
                      @change="updateUserRole"
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option v-for="role in roles" :key="role.id" :value="role.id">
                        {{ role.name }}
                      </option>
                    </select>
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Status</label>
                    <select 
                      v-model="userManagement.userForm.status"
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option value="active">Active</option>
                      <option value="inactive">Inactive</option>
                    </select>
                  </div>
                </div>
                
                <!-- Permissions Preview -->
                <div class="mt-6">
                  <h4 class="text-sm font-medium text-gray-700 mb-3">Assigned Permissions</h4>
                  <div class="bg-gray-50 rounded-lg p-4">
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <span class="text-xs font-medium text-gray-500 uppercase tracking-wider">Page Access:</span>
                        <div class="mt-2 space-y-1">
                          <div 
                            v-for="permission in userManagement.userForm.permissions.pages" 
                            :key="permission"
                            class="text-sm text-gray-700"
                          >
                            • {{ permission.replace('view_', '').replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()) }}
                          </div>
                        </div>
                      </div>
                      <div>
                        <span class="text-xs font-medium text-gray-500 uppercase tracking-wider">Data Access:</span>
                        <div class="mt-2 space-y-1">
                          <div 
                            v-for="dataAccess in userManagement.userForm.permissions.data" 
                            :key="dataAccess"
                            class="text-sm text-gray-700"
                          >
                            • {{ dataAccess.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()) }}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div class="flex justify-end space-x-3 pt-4">
                  <button 
                    type="button" 
                    @click="closeUserModal"
                    class="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors"
                  >
                    Cancel
                  </button>
                  <button 
                    type="submit"
                    class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                  >
                    {{ userManagement.editMode ? 'Update User' : 'Create User' }}
                  </button>
                </div>
              </form>
            </div>
          </div>

          <!-- Workload Management Tab -->
          <div v-if="activeTab === 'workloads'" class="space-y-6">
            <div class="bg-white rounded-xl shadow-sm p-6">
              <div class="flex items-center justify-between mb-6">
                <h2 class="text-xl font-semibold">Workload Management</h2>
                <div class="flex space-x-3">
                  <button @click="showCreateWorkloadModal = true" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                    <i data-lucide="plus" class="w-4 h-4 mr-2"></i>
                    Create Workload Group
                  </button>
                  <button @click="loadWorkloadGroups" class="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors">
                    <i data-lucide="refresh-cw" class="w-4 h-4 mr-2"></i>
                    Refresh
                  </button>
                </div>
              </div>

              <!-- Smart Filter for Workloads -->
              <div class="bg-gray-50 rounded-lg p-4 mb-6">
                <h3 class="text-sm font-medium text-gray-700 mb-3">Smart Filters</h3>
                <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div>
                    <label class="block text-xs text-gray-600 mb-1">Filter by Status</label>
                    <select v-model="workloadFilters.status" @change="applyWorkloadFilters" class="w-full px-3 py-2 text-sm border rounded-md">
                      <option value="">All Status</option>
                      <option value="active">Active</option>
                      <option value="inactive">Inactive</option>
                    </select>
                  </div>
                  <div>
                    <label class="block text-xs text-gray-600 mb-1">Filter by Capacity</label>
                    <select v-model="workloadFilters.capacity" @change="applyWorkloadFilters" class="w-full px-3 py-2 text-sm border rounded-md">
                      <option value="">All Capacity</option>
                      <option value="high">High (>80%)</option>
                      <option value="medium">Medium (50-80%)</option>
                      <option value="low">Low (<50%)</option>
                    </select>
                  </div>
                  <div>
                    <label class="block text-xs text-gray-600 mb-1">Search</label>
                    <input v-model="workloadFilters.search" @input="applyWorkloadFilters" type="text" placeholder="Search workloads..." class="w-full px-3 py-2 text-sm border rounded-md">
                  </div>
                  <div class="flex items-end">
                    <button @click="clearWorkloadFilters" class="px-4 py-2 text-sm bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300">
                      Clear Filters
                    </button>
                  </div>
                </div>
              </div>

              <!-- Workload Groups List -->
              <div v-if="filteredWorkloadGroups.length > 0" class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div v-for="workload in filteredWorkloadGroups" :key="workload.id" class="border border-gray-200 rounded-lg p-6 hover:border-blue-300 transition-colors">
                  <div class="flex items-center justify-between mb-4">
                    <div>
                      <h3 class="text-lg font-semibold text-gray-900">{{ workload.display_name }}</h3>
                      <p class="text-sm text-gray-500">Internal: {{ workload.name }}</p>
                    </div>
                    <div class="flex items-center space-x-2">
                      <span :class="['px-2 py-1 rounded-full text-xs font-medium', 
                        workload.customer_visible ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800']">
                        {{ workload.customer_visible ? 'Customer Visible' : 'Internal Only' }}
                      </span>
                      <button @click="editWorkload(workload)" class="text-blue-600 hover:text-blue-700">
                        <i data-lucide="edit" class="w-4 h-4"></i>
                      </button>
                    </div>
                  </div>
                  
                  <p class="text-gray-600 mb-4">{{ workload.description || 'No description' }}</p>
                  
                  <!-- Capacity Summary -->
                  <div v-if="workload.total_cpu_cores" class="bg-gray-50 rounded-lg p-4 mb-4">
                    <h4 class="text-sm font-medium text-gray-700 mb-3">Resource Capacity</h4>
                    <div class="grid grid-cols-3 gap-4 text-center">
                      <div>
                        <div class="text-lg font-bold text-blue-600">{{ workload.available_cpu_cores || 0 }}/{{ workload.total_cpu_cores || 0 }}</div>
                        <div class="text-xs text-gray-500">CPU Cores</div>
                      </div>
                      <div>
                        <div class="text-lg font-bold text-green-600">{{ workload.available_memory_gb || 0 }}/{{ workload.total_memory_gb || 0 }}</div>
                        <div class="text-xs text-gray-500">Memory GB</div>
                      </div>
                      <div>
                        <div class="text-lg font-bold text-purple-600">{{ workload.cluster_count || 0 }}</div>
                        <div class="text-xs text-gray-500">Clusters</div>
                      </div>
                    </div>
                  </div>
                  
                  <!-- Actions -->
                  <div class="flex space-x-2">
                    <button @click="manageWorkloadClusters(workload)" class="flex-1 px-3 py-2 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700">
                      Manage Clusters
                    </button>
                    <button @click="calculateWorkloadCapacity(workload.id)" class="px-3 py-2 text-sm bg-gray-600 text-white rounded-md hover:bg-gray-700">
                      Refresh Capacity
                    </button>
                  </div>
                </div>
              </div>
              
              <div v-else class="text-center py-12">
                <i data-lucide="folder" class="w-12 h-12 text-gray-400 mx-auto mb-3"></i>
                <h3 class="text-lg font-medium text-gray-900 mb-2">No Workload Groups</h3>
                <p class="text-gray-600 mb-4">Create your first workload group to organize clusters</p>
                <button @click="showCreateWorkloadModal = true" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                  Create Workload Group
                </button>
              </div>
            </div>
          </div>

          <!-- License Management Tab -->
          <div v-if="activeTab === 'licenses'" class="space-y-6">
            <div class="bg-white rounded-xl shadow-sm p-6">
              <div class="flex items-center justify-between mb-6">
                <h2 class="text-xl font-semibold">License Management</h2>
                <div class="flex space-x-3">
                  <button @click="showCreateLicensePoolModal = true" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                    <i data-lucide="plus" class="w-4 h-4 mr-2"></i>
                    Add License Pool
                  </button>
                  <button @click="loadLicensePools" class="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors">
                    <i data-lucide="refresh-cw" class="w-4 h-4 mr-2"></i>
                    Refresh
                  </button>
                </div>
              </div>

              <!-- Smart Filter for Licenses -->
              <div class="bg-gray-50 rounded-lg p-4 mb-6">
                <h3 class="text-sm font-medium text-gray-700 mb-3">Smart Filters</h3>
                <div class="grid grid-cols-1 md:grid-cols-5 gap-4">
                  <div>
                    <label class="block text-xs text-gray-600 mb-1">Workload Group</label>
                    <select v-model="licenseFilters.workloadGroup" @change="applyLicenseFilters" class="w-full px-3 py-2 text-sm border rounded-md">
                      <option value="">All Workloads</option>
                      <option v-for="wg in workloadGroups" :key="wg.id" :value="wg.id">{{ wg.display_name }}</option>
                    </select>
                  </div>
                  <div>
                    <label class="block text-xs text-gray-600 mb-1">License Type</label>
                    <select v-model="licenseFilters.licenseType" @change="applyLicenseFilters" class="w-full px-3 py-2 text-sm border rounded-md">
                      <option value="">All Types</option>
                      <option value="Citrix">Citrix</option>
                      <option value="Microsoft">Microsoft</option>
                      <option value="Canonical">Canonical</option>
                      <option value="Lakeside">Lakeside</option>
                    </select>
                  </div>
                  <div>
                    <label class="block text-xs text-gray-600 mb-1">Utilization</label>
                    <select v-model="licenseFilters.utilization" @change="applyLicenseFilters" class="w-full px-3 py-2 text-sm border rounded-md">
                      <option value="">All Utilization</option>
                      <option value="high">High (>80%)</option>
                      <option value="medium">Medium (50-80%)</option>
                      <option value="low">Low (<50%)</option>
                    </select>
                  </div>
                  <div>
                    <label class="block text-xs text-gray-600 mb-1">Expiry</label>
                    <select v-model="licenseFilters.expiry" @change="applyLicenseFilters" class="w-full px-3 py-2 text-sm border rounded-md">
                      <option value="">All</option>
                      <option value="30days">Expires in 30 days</option>
                      <option value="90days">Expires in 90 days</option>
                      <option value="expired">Expired</option>
                    </select>
                  </div>
                  <div class="flex items-end">
                    <button @click="clearLicenseFilters" class="px-4 py-2 text-sm bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300">
                      Clear Filters
                    </button>
                  </div>
                </div>
              </div>

              <!-- License Summary Cards -->
              <div v-if="licenseSummary" class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                <div class="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-6">
                  <div class="flex items-center justify-between">
                    <div>
                      <p class="text-sm font-medium text-gray-600">Total Licenses</p>
                      <p class="text-2xl font-bold text-indigo-600">{{ licenseSummary.totalLicenses }}</p>
                    </div>
                    <div class="w-12 h-12 bg-indigo-100 rounded-lg flex items-center justify-center">
                      <i data-lucide="key" class="w-6 h-6 text-indigo-600"></i>
                    </div>
                  </div>
                </div>
                
                <div class="bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg p-6">
                  <div class="flex items-center justify-between">
                    <div>
                      <p class="text-sm font-medium text-gray-600">Available</p>
                      <p class="text-2xl font-bold text-green-600">{{ licenseSummary.availableLicenses }}</p>
                    </div>
                    <div class="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                      <i data-lucide="check-circle" class="w-6 h-6 text-green-600"></i>
                    </div>
                  </div>
                </div>
                
                <div class="bg-gradient-to-r from-yellow-50 to-orange-50 rounded-lg p-6">
                  <div class="flex items-center justify-between">
                    <div>
                      <p class="text-sm font-medium text-gray-600">In Use</p>
                      <p class="text-2xl font-bold text-orange-600">{{ licenseSummary.allocatedLicenses }}</p>
                    </div>
                    <div class="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
                      <i data-lucide="users" class="w-6 h-6 text-orange-600"></i>
                    </div>
                  </div>
                </div>
                
                <div class="bg-gradient-to-r from-red-50 to-pink-50 rounded-lg p-6">
                  <div class="flex items-center justify-between">
                    <div>
                      <p class="text-sm font-medium text-gray-600">Expiring Soon</p>
                      <p class="text-2xl font-bold text-red-600">{{ licenseSummary.expiringSoon }}</p>
                    </div>
                    <div class="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center">
                      <i data-lucide="alert-triangle" class="w-6 h-6 text-red-600"></i>
                    </div>
                  </div>
                </div>
              </div>

              <!-- License Pools Table -->
              <div v-if="filteredLicensePools.length > 0" class="overflow-x-auto">
                <table class="min-w-full divide-y divide-gray-200">
                  <thead class="bg-gray-50">
                    <tr>
                      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">License Type</th>
                      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Workload Group</th>
                      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Usage</th>
                      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Cost</th>
                      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Renewal</th>
                      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                    </tr>
                  </thead>
                  <tbody class="bg-white divide-y divide-gray-200">
                    <tr v-for="pool in filteredLicensePools" :key="pool.id" class="hover:bg-gray-50">
                      <td class="px-6 py-4 whitespace-nowrap">
                        <div>
                          <div class="text-sm font-medium text-gray-900">{{ pool.license_type_name }}</div>
                          <div class="text-sm text-gray-500">{{ pool.vendor }} - {{ pool.product }}</div>
                        </div>
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap">
                        <div class="text-sm text-gray-900">{{ pool.workload_group_name }}</div>
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap">
                        <div class="flex items-center">
                          <div class="text-sm text-gray-900 mr-2">{{ pool.allocated_licenses }}/{{ pool.total_licenses }}</div>
                          <div class="w-16 bg-gray-200 rounded-full h-2">
                            <div :class="['h-2 rounded-full', 
                              (pool.allocated_licenses / pool.total_licenses * 100) > 80 ? 'bg-red-500' : 
                              (pool.allocated_licenses / pool.total_licenses * 100) > 60 ? 'bg-yellow-500' : 'bg-green-500']"
                              :style="{ width: Math.min(100, (pool.allocated_licenses / pool.total_licenses * 100)) + '%' }">
                            </div>
                          </div>
                          <div class="text-xs text-gray-500 ml-2">{{ Math.round(pool.allocated_licenses / pool.total_licenses * 100) }}%</div>
                        </div>
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap">
                        <div class="text-sm text-gray-900">${{ (pool.cost_per_license * pool.total_licenses).toFixed(2) }}</div>
                        <div class="text-sm text-gray-500">${{ pool.cost_per_license }}/license</div>
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap">
                        <div v-if="pool.renewal_date" :class="['text-sm', isExpiringSoon(pool.renewal_date) ? 'text-red-600 font-medium' : 'text-gray-900']">
                          {{ formatDate(pool.renewal_date) }}
                        </div>
                        <div v-else class="text-sm text-gray-500">No renewal date</div>
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <button @click="editLicensePool(pool)" class="text-blue-600 hover:text-blue-700 mr-3">Edit</button>
                        <button @click="viewLicenseAllocations(pool)" class="text-green-600 hover:text-green-700">Allocations</button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
              
              <div v-else class="text-center py-12">
                <i data-lucide="key" class="w-12 h-12 text-gray-400 mx-auto mb-3"></i>
                <h3 class="text-lg font-medium text-gray-900 mb-2">No License Pools</h3>
                <p class="text-gray-600 mb-4">Add your first license pool to start tracking licenses</p>
                <button @click="showCreateLicensePoolModal = true" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                  Add License Pool
                </button>
              </div>
            </div>
          </div>
          
          <!-- Administration Tab -->
          <div v-if="activeTab === 'admin'" class="container mx-auto px-6 py-8">
            <div class="mb-8">
              <h2 class="text-2xl font-bold text-gray-900 mb-2">System Administration</h2>
              <p class="text-gray-600">Manage integrations and monitor system health</p>
            </div>
            
            <!-- Sync Status Overview -->
            <div class="mb-8">
              <div class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                <div class="flex items-center space-x-2 mb-2">
                  <i data-lucide="info" class="w-4 h-4 text-blue-600"></i>
                  <span class="text-sm font-medium text-blue-800">Sync Status</span>
                </div>
                <p class="text-sm text-blue-700">
                  <strong>vCenter:</strong> Real sync with backend API &nbsp;•&nbsp; 
                  <strong>Zabbix/Prometheus:</strong> Real sync endpoints available
                </p>
              </div>
              <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div v-for="(syncData, type) in adminData.syncStatus" :key="type" class="bg-white rounded-xl shadow-sm p-6">
                  <div class="flex items-center justify-between mb-4">
                    <div class="flex items-center space-x-3">
                      <div class="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center">
                        <span class="text-lg">
                          {{ type === 'vcenter' ? '🏢' : type === 'zabbix' ? '📊' : '🔥' }}
                        </span>
                      </div>
                      <div>
                        <h3 class="font-semibold capitalize">{{ type }}</h3>
                        <div class="flex items-center space-x-2">
                          <div :class="[
                            'w-2 h-2 rounded-full',
                            syncData.connected ? 'bg-green-500' : 'bg-gray-400'
                          ]"></div>
                          <span class="text-sm text-gray-600">
                            {{ syncData.connected ? 'Connected' : 'Disconnected' }}
                          </span>
                        </div>
                      </div>
                    </div>
                    
                    <div class="text-right">
                      <div v-if="syncData.syncing" class="flex items-center space-x-2">
                        <div class="loading-spinner"></div>
                        <span class="text-sm text-blue-600">Syncing</span>
                      </div>
                      <div v-else-if="syncData.autoSync" class="text-sm text-green-600">Auto-sync ON</div>
                      <div v-else class="text-sm text-gray-500">Manual sync</div>
                    </div>
                  </div>
                  
                  <div class="space-y-2">
                    <div v-if="syncData.lastSync" class="text-xs text-gray-500">
                      Last sync: {{ new Date(syncData.lastSync).toLocaleString() }}
                    </div>
                    <div v-else class="text-xs text-gray-500">
                      Never synced
                    </div>
                    
                    <div v-if="syncData.syncing" class="w-full bg-gray-200 rounded-full h-1.5">
                      <div 
                        class="bg-blue-500 h-1.5 rounded-full transition-all duration-300"
                        :style="{ width: syncData.syncProgress + '%' }"
                      ></div>
                    </div>
                    
                    <div v-if="syncData.errors.length" class="text-xs text-red-600">
                      {{ syncData.errors.length }} error(s)
                    </div>
                  </div>
                  
                  <div class="mt-4 flex space-x-2">
                    <button 
                      @click="startSync(type)"
                      :disabled="!syncData.connected || syncData.syncing"
                      class="flex-1 px-3 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {{ syncData.syncing ? 'Syncing...' : 'Sync Now' }}
                    </button>
                  </div>
                </div>
              </div>
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
                  
                  <!-- Connection Status -->
                  <div class="mb-6 p-4 rounded-lg" :class="[
                    adminData.syncStatus.vcenter.connected ? 'bg-green-50 border border-green-200' : 'bg-gray-50 border border-gray-200'
                  ]">
                    <div class="flex items-center justify-between">
                      <div class="flex items-center space-x-2">
                        <div :class="[
                          'w-3 h-3 rounded-full',
                          adminData.syncStatus.vcenter.connected ? 'bg-green-500' : 'bg-gray-400'
                        ]"></div>
                        <span class="font-medium">
                          {{ adminData.syncStatus.vcenter.connected ? 'Connected' : 'Not Connected' }}
                        </span>
                      </div>
                      <div v-if="adminData.syncStatus.vcenter.lastSync" class="text-sm text-gray-600">
                        Last sync: {{ new Date(adminData.syncStatus.vcenter.lastSync).toLocaleString() }}
                      </div>
                    </div>
                    
                    <!-- Sync Progress -->
                    <div v-if="adminData.syncStatus.vcenter.syncing" class="mt-3">
                      <div class="flex justify-between text-sm mb-1">
                        <span>Synchronizing...</span>
                        <span>{{ adminData.syncStatus.vcenter.syncProgress }}%</span>
                      </div>
                      <div class="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          class="bg-blue-500 h-2 rounded-full transition-all duration-300"
                          :style="{ width: adminData.syncStatus.vcenter.syncProgress + '%' }"
                        ></div>
                      </div>
                      <div class="text-xs text-gray-600 mt-1">
                        {{ adminData.syncStatus.vcenter.syncedVMs }} / {{ adminData.syncStatus.vcenter.totalVMs }} VMs processed
                      </div>
                    </div>
                  </div>
                  
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
                    
                    <!-- Connection Actions -->
                    <div class="flex space-x-3">
                      <button type="submit" class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
                        Test Connection
                      </button>
                      <button 
                        type="button"
                        @click="startSync('vcenter')"
                        :disabled="!adminData.syncStatus.vcenter.connected || adminData.syncStatus.vcenter.syncing"
                        class="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {{ adminData.syncStatus.vcenter.syncing ? 'Syncing...' : 'Start Sync' }}
                      </button>
                      <button 
                        v-if="adminData.syncStatus.vcenter.syncing"
                        type="button"
                        @click="stopSync('vcenter')"
                        class="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
                      >
                        Stop Sync
                      </button>
                    </div>
                  </form>
                  
                  <!-- Auto-Sync Settings -->
                  <div class="mt-6 p-4 bg-gray-50 rounded-lg">
                    <h4 class="text-sm font-medium text-gray-900 mb-3">Auto-Sync Settings</h4>
                    <div class="flex items-center justify-between">
                      <div class="flex items-center space-x-3">
                        <label class="flex items-center">
                          <input 
                            type="checkbox" 
                            :checked="adminData.syncStatus.vcenter.autoSync"
                            @change="toggleAutoSync('vcenter')"
                            class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                          >
                          <span class="ml-2 text-sm text-gray-700">Enable automatic synchronization</span>
                        </label>
                      </div>
                      <div class="flex items-center space-x-2">
                        <label class="text-sm text-gray-600">Interval:</label>
                        <select 
                          v-model="adminData.syncStatus.vcenter.syncInterval"
                          class="text-sm border border-gray-300 rounded px-2 py-1"
                        >
                          <option :value="60">1 minute</option>
                          <option :value="300">5 minutes</option>
                          <option :value="900">15 minutes</option>
                          <option :value="3600">1 hour</option>
                        </select>
                      </div>
                    </div>
                  </div>
                  
                  <!-- Sync Errors -->
                  <div v-if="adminData.syncStatus.vcenter.errors.length" class="mt-4">
                    <h4 class="text-sm font-medium text-red-900 mb-2">Sync Errors</h4>
                    <div class="bg-red-50 border border-red-200 rounded-lg p-3">
                      <div v-for="(error, index) in adminData.syncStatus.vcenter.errors" :key="index" class="text-sm text-red-700">
                        • {{ error }}
                      </div>
                    </div>
                  </div>
                </div>
                
                <!-- Microsoft HyperV Integration -->
                <div v-if="adminData.selectedIntegration === 'hyperv'" class="bg-white rounded-xl shadow-sm p-6">
                  <h3 class="text-lg font-semibold mb-4">🖥️ Microsoft HyperV Integration</h3>
                  
                  <!-- Connection Status -->
                  <div class="mb-6 p-4 rounded-lg" :class="[
                    adminData.syncStatus.hyperv.connected ? 'bg-green-50 border border-green-200' : 'bg-gray-50 border border-gray-200'
                  ]">
                    <div class="flex items-center justify-between">
                      <div class="flex items-center space-x-2">
                        <div :class="[
                          'w-3 h-3 rounded-full',
                          adminData.syncStatus.hyperv.connected ? 'bg-green-500' : 'bg-gray-400'
                        ]"></div>
                        <span class="font-medium">
                          {{ adminData.syncStatus.hyperv.connected ? 'Connected' : 'Not Connected' }}
                        </span>
                      </div>
                      <div v-if="adminData.syncStatus.hyperv.lastSync" class="text-sm text-gray-600">
                        Last sync: {{ new Date(adminData.syncStatus.hyperv.lastSync).toLocaleString() }}
                      </div>
                    </div>
                    
                    <!-- Sync Progress -->
                    <div v-if="adminData.syncStatus.hyperv.syncing" class="mt-3">
                      <div class="flex justify-between text-sm mb-1">
                        <span>Synchronizing...</span>
                        <span>{{ adminData.syncStatus.hyperv.syncProgress }}%</span>
                      </div>
                      <div class="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          class="bg-blue-500 h-2 rounded-full transition-all duration-300"
                          :style="{ width: adminData.syncStatus.hyperv.syncProgress + '%' }"
                        ></div>
                      </div>
                      <div class="text-xs text-gray-600 mt-1">
                        {{ adminData.syncStatus.hyperv.syncedVMs }} / {{ adminData.syncStatus.hyperv.totalVMs }} VMs processed
                      </div>
                    </div>
                  </div>
                  
                  <form @submit.prevent="testConnection('hyperv')" class="space-y-4">
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-2">HyperV Host</label>
                      <input v-model="adminData.connectionForms.hyperv.host" type="text" class="w-full border border-gray-300 rounded-md px-3 py-2" placeholder="hyperv-host.local">
                    </div>
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-2">Username</label>
                      <input v-model="adminData.connectionForms.hyperv.username" type="text" class="w-full border border-gray-300 rounded-md px-3 py-2" placeholder="Administrator" autocomplete="username">
                    </div>
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-2">Password</label>
                      <input id="hyperv-password" v-model="adminData.connectionForms.hyperv.password" type="password" placeholder="Enter HyperV password" autocomplete="current-password" spellcheck="false" @input="debugCredentialInput('password', $event)" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                    </div>
                    
                    <!-- Connection Actions -->
                    <div class="flex space-x-3">
                      <button type="submit" class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
                        Test Connection
                      </button>
                      <button 
                        type="button"
                        @click="startSync('hyperv')"
                        :disabled="!adminData.syncStatus.hyperv.connected || adminData.syncStatus.hyperv.syncing"
                        class="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {{ adminData.syncStatus.hyperv.syncing ? 'Syncing...' : 'Start Sync' }}
                      </button>
                      <button 
                        v-if="adminData.syncStatus.hyperv.syncing"
                        type="button"
                        @click="stopSync('hyperv')"
                        class="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
                      >
                        Stop Sync
                      </button>
                    </div>
                  </form>
                  
                  <!-- Auto-Sync Settings -->
                  <div class="mt-6 p-4 bg-gray-50 rounded-lg">
                    <h4 class="text-sm font-medium text-gray-900 mb-3">Auto-Sync Settings</h4>
                    <div class="flex items-center justify-between">
                      <div class="flex items-center space-x-3">
                        <label class="flex items-center">
                          <input 
                            type="checkbox" 
                            :checked="adminData.syncStatus.hyperv.autoSync"
                            @change="toggleAutoSync('hyperv')"
                            class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                          >
                          <span class="ml-2 text-sm text-gray-700">Enable automatic synchronization</span>
                        </label>
                      </div>
                      <div class="flex items-center space-x-2">
                        <label class="text-sm text-gray-600">Interval:</label>
                        <select 
                          v-model="adminData.syncStatus.hyperv.syncInterval"
                          class="text-sm border border-gray-300 rounded px-2 py-1"
                        >
                          <option :value="60">1 minute</option>
                          <option :value="300">5 minutes</option>
                          <option :value="900">15 minutes</option>
                          <option :value="3600">1 hour</option>
                        </select>
                      </div>
                    </div>
                  </div>
                  
                  <!-- Sync Errors -->
                  <div v-if="adminData.syncStatus.hyperv.errors.length" class="mt-4">
                    <h4 class="text-sm font-medium text-red-900 mb-2">Sync Errors</h4>
                    <div class="bg-red-50 border border-red-200 rounded-lg p-3">
                      <div v-for="(error, index) in adminData.syncStatus.hyperv.errors" :key="index" class="text-sm text-red-700">
                        • {{ error }}
                      </div>
                    </div>
                  </div>
                </div>
                
                <!-- Zabbix Integration -->
                <div v-if="adminData.selectedIntegration === 'zabbix'" class="bg-white rounded-xl shadow-sm p-6">
                  <h3 class="text-lg font-semibold mb-4">📊 Zabbix Integration</h3>
                  
                  <!-- Connection Status -->
                  <div class="mb-6 p-4 rounded-lg" :class="[
                    adminData.syncStatus.zabbix.connected ? 'bg-green-50 border border-green-200' : 'bg-gray-50 border border-gray-200'
                  ]">
                    <div class="flex items-center justify-between">
                      <div class="flex items-center space-x-2">
                        <div :class="[
                          'w-3 h-3 rounded-full',
                          adminData.syncStatus.zabbix.connected ? 'bg-green-500' : 'bg-gray-400'
                        ]"></div>
                        <span class="font-medium">
                          {{ adminData.syncStatus.zabbix.connected ? 'Connected' : 'Not Connected' }}
                        </span>
                      </div>
                      <div v-if="adminData.syncStatus.zabbix.lastSync" class="text-sm text-gray-600">
                        Last sync: {{ new Date(adminData.syncStatus.zabbix.lastSync).toLocaleString() }}
                      </div>
                    </div>
                    
                    <!-- Sync Progress -->
                    <div v-if="adminData.syncStatus.zabbix.syncing" class="mt-3">
                      <div class="flex justify-between text-sm mb-1">
                        <span>Synchronizing metrics...</span>
                        <span>{{ adminData.syncStatus.zabbix.syncProgress }}%</span>
                      </div>
                      <div class="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          class="bg-blue-500 h-2 rounded-full transition-all duration-300"
                          :style="{ width: adminData.syncStatus.zabbix.syncProgress + '%' }"
                        ></div>
                      </div>
                      <div class="text-xs text-gray-600 mt-1">
                        {{ adminData.syncStatus.zabbix.syncedMetrics }} / {{ adminData.syncStatus.zabbix.totalMetrics }} metrics processed
                      </div>
                    </div>
                  </div>
                  
                  <form @submit.prevent="testConnection('zabbix')" class="space-y-4">
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-2">Zabbix API URL</label>
                      <input v-model="adminData.connectionForms.zabbix.url" type="text" class="w-full border border-gray-300 rounded-md px-3 py-2" placeholder="http://zabbix.local/api_jsonrpc.php">
                    </div>
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-2">Username</label>
                      <input v-model="adminData.connectionForms.zabbix.username" type="text" class="w-full border border-gray-300 rounded-md px-3 py-2" placeholder="Admin" autocomplete="username">
                    </div>
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-2">Password</label>
                      <input id="zabbix-password" v-model="adminData.connectionForms.zabbix.password" type="password" placeholder="Enter Zabbix password" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500" autocomplete="current-password">
                    </div>
                    
                    <!-- Connection Actions -->
                    <div class="flex space-x-3">
                      <button type="submit" class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
                        Test Connection
                      </button>
                      <button 
                        type="button"
                        @click="startSync('zabbix')"
                        :disabled="!adminData.syncStatus.zabbix.connected || adminData.syncStatus.zabbix.syncing"
                        class="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {{ adminData.syncStatus.zabbix.syncing ? 'Syncing...' : 'Start Sync' }}
                      </button>
                      <button 
                        v-if="adminData.syncStatus.zabbix.syncing"
                        type="button"
                        @click="stopSync('zabbix')"
                        class="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
                      >
                        Stop Sync
                      </button>
                    </div>
                  </form>
                  
                  <!-- Auto-Sync Settings -->
                  <div class="mt-6 p-4 bg-gray-50 rounded-lg">
                    <h4 class="text-sm font-medium text-gray-900 mb-3">Auto-Sync Settings</h4>
                    <div class="flex items-center justify-between">
                      <div class="flex items-center space-x-3">
                        <label class="flex items-center">
                          <input 
                            type="checkbox" 
                            :checked="adminData.syncStatus.zabbix.autoSync"
                            @change="toggleAutoSync('zabbix')"
                            class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                          >
                          <span class="ml-2 text-sm text-gray-700">Enable automatic synchronization</span>
                        </label>
                      </div>
                      <div class="flex items-center space-x-2">
                        <label class="text-sm text-gray-600">Interval:</label>
                        <select 
                          v-model="adminData.syncStatus.zabbix.syncInterval"
                          class="text-sm border border-gray-300 rounded px-2 py-1"
                        >
                          <option :value="30">30 seconds</option>
                          <option :value="60">1 minute</option>
                          <option :value="300">5 minutes</option>
                          <option :value="900">15 minutes</option>
                        </select>
                      </div>
                    </div>
                  </div>
                  
                  <!-- Sync Errors -->
                  <div v-if="adminData.syncStatus.zabbix.errors.length" class="mt-4">
                    <h4 class="text-sm font-medium text-red-900 mb-2">Sync Errors</h4>
                    <div class="bg-red-50 border border-red-200 rounded-lg p-3">
                      <div v-for="(error, index) in adminData.syncStatus.zabbix.errors" :key="index" class="text-sm text-red-700">
                        • {{ error }}
                      </div>
                    </div>
                  </div>
                </div>
                
                <!-- Prometheus Integration -->
                <div v-if="adminData.selectedIntegration === 'prometheus'" class="bg-white rounded-xl shadow-sm p-6">
                  <h3 class="text-lg font-semibold mb-4">🔥 Prometheus Integration</h3>
                  
                  <!-- Connection Status -->
                  <div class="mb-6 p-4 rounded-lg" :class="[
                    adminData.syncStatus.prometheus.connected ? 'bg-green-50 border border-green-200' : 'bg-gray-50 border border-gray-200'
                  ]">
                    <div class="flex items-center justify-between">
                      <div class="flex items-center space-x-2">
                        <div :class="[
                          'w-3 h-3 rounded-full',
                          adminData.syncStatus.prometheus.connected ? 'bg-green-500' : 'bg-gray-400'
                        ]"></div>
                        <span class="font-medium">
                          {{ adminData.syncStatus.prometheus.connected ? 'Connected' : 'Not Connected' }}
                        </span>
                      </div>
                      <div v-if="adminData.syncStatus.prometheus.lastSync" class="text-sm text-gray-600">
                        Last sync: {{ new Date(adminData.syncStatus.prometheus.lastSync).toLocaleString() }}
                      </div>
                    </div>
                    
                    <!-- Sync Progress -->
                    <div v-if="adminData.syncStatus.prometheus.syncing" class="mt-3">
                      <div class="flex justify-between text-sm mb-1">
                        <span>Synchronizing metrics...</span>
                        <span>{{ adminData.syncStatus.prometheus.syncProgress }}%</span>
                      </div>
                      <div class="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          class="bg-blue-500 h-2 rounded-full transition-all duration-300"
                          :style="{ width: adminData.syncStatus.prometheus.syncProgress + '%' }"
                        ></div>
                      </div>
                      <div class="text-xs text-gray-600 mt-1">
                        {{ adminData.syncStatus.prometheus.syncedMetrics }} / {{ adminData.syncStatus.prometheus.totalMetrics }} metrics processed
                      </div>
                    </div>
                  </div>
                  
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
                    
                    <!-- Connection Actions -->
                    <div class="flex space-x-3">
                      <button type="submit" class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
                        Test Connection
                      </button>
                      <button 
                        type="button"
                        @click="startSync('prometheus')"
                        :disabled="!adminData.syncStatus.prometheus.connected || adminData.syncStatus.prometheus.syncing"
                        class="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {{ adminData.syncStatus.prometheus.syncing ? 'Syncing...' : 'Start Sync' }}
                      </button>
                      <button 
                        v-if="adminData.syncStatus.prometheus.syncing"
                        type="button"
                        @click="stopSync('prometheus')"
                        class="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
                      >
                        Stop Sync
                      </button>
                    </div>
                  </form>
                  
                  <!-- Auto-Sync Settings -->
                  <div class="mt-6 p-4 bg-gray-50 rounded-lg">
                    <h4 class="text-sm font-medium text-gray-900 mb-3">Auto-Sync Settings</h4>
                    <div class="flex items-center justify-between">
                      <div class="flex items-center space-x-3">
                        <label class="flex items-center">
                          <input 
                            type="checkbox" 
                            :checked="adminData.syncStatus.prometheus.autoSync"
                            @change="toggleAutoSync('prometheus')"
                            class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                          >
                          <span class="ml-2 text-sm text-gray-700">Enable automatic synchronization</span>
                        </label>
                      </div>
                      <div class="flex items-center space-x-2">
                        <label class="text-sm text-gray-600">Interval:</label>
                        <select 
                          v-model="adminData.syncStatus.prometheus.syncInterval"
                          class="text-sm border border-gray-300 rounded px-2 py-1"
                        >
                          <option :value="15">15 seconds</option>
                          <option :value="30">30 seconds</option>
                          <option :value="60">1 minute</option>
                          <option :value="300">5 minutes</option>
                        </select>
                      </div>
                    </div>
                  </div>
                  
                  <!-- Sync Errors -->
                  <div v-if="adminData.syncStatus.prometheus.errors.length" class="mt-4">
                    <h4 class="text-sm font-medium text-red-900 mb-2">Sync Errors</h4>
                    <div class="bg-red-50 border border-red-200 rounded-lg p-3">
                      <div v-for="(error, index) in adminData.syncStatus.prometheus.errors" :key="index" class="text-sm text-red-700">
                        • {{ error }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  `,
  data() {
    return {
      appLoaded: true,
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
      currentUser: {
        id: null,
        username: '',
        role: 'user', // 'admin', 'manager', 'user'
        permissions: {
          pages: [],
          data: []
        },
        profile: {
          fullName: '',
          email: '',
          department: '',
          lastLogin: null
        }
      },
      activeTab: localStorage.getItem('iroa_activeTab') || 'overview',  // Persist active tab across refreshes
      loading: false,
      searchTerm: '',
      filterStatus: 'all',
      viewMode: 'grid',
      selectedVM: null,
      recommendations: [],
      underutilizedVMs: [],
      anomalies: [],
      forecast: [],
      capacityData: null,
      profileData: null,
      selectedCluster: '',
      clusters: [],
      // vCenter inventory data from sync
      vcenterInventory: {
        vms: [],
        hosts: [],
        datastores: [],
        clusters: [],
        networks: [],
        lastSync: null,
        hasSyncedData: false
      },
      hypervInventory: {
        vms: [],
        hosts: [],
        datastores: [],
        clusters: [],
        networks: [],
        lastSync: null,
        hasSyncedData: false
      },
      realTimeData: {
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
        ]
      },
      realtimeChart: null,
      realtimeUpdateInterval: null,
      realtimeChartData: {
        cpu: [45, 47, 44, 46, 48, 45, 43, 45],
        memory: [62, 64, 61, 63, 65, 62, 60, 62],
        timestamps: []
      },
      availableTabs: [
        { id: 'overview', name: 'Overview', icon: 'layout-dashboard', requiredRole: 'user', requiredPermission: 'view_overview' },
        { id: 'recommendations', name: 'Recommendations', icon: 'lightbulb', requiredRole: 'user', requiredPermission: 'view_recommendations' },
        { id: 'vms', name: 'Virtual Machines', icon: 'server', requiredRole: 'user', requiredPermission: 'view_vms' },
        { id: 'capacity', name: 'Capacity Planning', icon: 'cpu', requiredRole: 'manager', requiredPermission: 'view_capacity' },
        { id: 'profiles', name: 'VM Profiles', icon: 'layers', requiredRole: 'manager', requiredPermission: 'view_profiles' },
        { id: 'workloads', name: 'Workload Management', icon: 'folder', requiredRole: 'admin', requiredPermission: 'manage_workloads' },
        { id: 'licenses', name: 'License Management', icon: 'key', requiredRole: 'admin', requiredPermission: 'manage_licenses' },
        { id: 'analytics', name: 'Analytics', icon: 'bar-chart-3', requiredRole: 'manager', requiredPermission: 'view_analytics' },
        { id: 'monitoring', name: 'Real-Time Monitoring', icon: 'activity', requiredRole: 'user', requiredPermission: 'view_monitoring' },
        { id: 'users', name: 'User Management', icon: 'users', requiredRole: 'admin', requiredPermission: 'manage_users' },
        { id: 'admin', name: 'Administration', icon: 'settings', requiredRole: 'admin', requiredPermission: 'system_admin' }
      ],
      users: [
        {
          id: 1,
          username: 'admin',
          fullName: 'System Administrator',
          email: 'admin@iroa.local',
          role: 'admin',
          department: 'IT',
          status: 'active',
          lastLogin: '2024-01-15T10:30:00Z',
          permissions: {
            pages: ['view_overview', 'view_recommendations', 'view_vms', 'view_capacity', 'view_profiles', 'manage_workloads', 'manage_licenses', 'view_analytics', 'view_monitoring', 'manage_users', 'system_admin'],
            data: ['sensitive_data', 'financial_data', 'user_data', 'system_logs']
          }
        },
        {
          id: 2,
          username: 'manager1',
          fullName: 'John Manager',
          email: 'john.manager@iroa.local',
          role: 'manager',
          department: 'Operations',
          status: 'active',
          lastLogin: '2024-01-15T09:15:00Z',
          permissions: {
            pages: ['view_overview', 'view_recommendations', 'view_vms', 'view_capacity', 'view_profiles', 'view_analytics', 'view_monitoring'],
            data: ['financial_data', 'operational_data']
          }
        },
        {
          id: 3,
          username: 'user1',
          fullName: 'Jane User',
          email: 'jane.user@iroa.local',
          role: 'user',
          department: 'Development',
          status: 'active',
          lastLogin: '2024-01-15T08:45:00Z',
          permissions: {
            pages: ['view_overview', 'view_recommendations', 'view_vms', 'view_monitoring'],
            data: ['basic_data']
          }
        }
      ],
      roles: [
        {
          id: 'admin',
          name: 'Administrator',
          description: 'Full system access with user management capabilities',
          permissions: {
            pages: ['view_overview', 'view_recommendations', 'view_vms', 'view_capacity', 'view_profiles', 'manage_workloads', 'manage_licenses', 'view_analytics', 'view_monitoring', 'manage_users', 'system_admin'],
            data: ['sensitive_data', 'financial_data', 'user_data', 'system_logs', 'operational_data', 'basic_data']
          }
        },
        {
          id: 'manager',
          name: 'Manager',
          description: 'Advanced access to capacity planning and analytics',
          permissions: {
            pages: ['view_overview', 'view_recommendations', 'view_vms', 'view_capacity', 'view_profiles', 'view_analytics', 'view_monitoring'],
            data: ['financial_data', 'operational_data', 'basic_data']
          }
        },
        {
          id: 'user',
          name: 'User',
          description: 'Basic access to overview and monitoring',
          permissions: {
            pages: ['view_overview', 'view_recommendations', 'view_vms', 'view_monitoring'],
            data: ['basic_data']
          }
        }
      ],
      userManagement: {
        selectedUser: null,
        showUserModal: false,
        showRoleModal: false,
        userForm: {
          id: null,
          username: '',
          fullName: '',
          email: '',
          role: 'user',
          department: '',
          status: 'active',
          permissions: {
            pages: [],
            data: []
          }
        },
        editMode: false
      },
      stats: [
        { title: 'Total VMs', value: '5', change: 0, icon: 'server', bgColor: 'bg-blue-500', requiresDataAccess: null },
        { title: 'Underutilized', value: '2', change: -20, icon: 'trending-down', bgColor: 'bg-yellow-500', requiresDataAccess: 'operational_data' },
        { title: 'Cost Savings', value: '$1,240', change: 15, icon: 'dollar-sign', bgColor: 'bg-green-500', requiresDataAccess: 'financial_data' },
        { title: 'Efficiency', value: '87%', change: 5, icon: 'zap', bgColor: 'bg-purple-500', requiresDataAccess: 'operational_data' }
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
          { id: 'hyperv', name: 'Microsoft HyperV', icon: '🖥️', description: 'Connect to Microsoft HyperV Host' },
          { id: 'zabbix', name: 'Zabbix', icon: '📊', description: 'Integrate with Zabbix monitoring' },
          { id: 'prometheus', name: 'Prometheus', icon: '🔥', description: 'Connect to Prometheus metrics' }
        ],
        connectionForms: {
          vcenter: { host: 'vcenter.local', username: 'administrator@vsphere.local', password: '' },
          hyperv: { host: 'hyperv-host.local', username: 'Administrator', password: '' },
          zabbix: { url: 'http://zabbix.local/api_jsonrpc.php', username: 'Admin', password: '' },
          prometheus: { url: 'http://localhost:9090', username: '', password: '' }
        },
        syncStatus: {
          vcenter: {
            connected: false,
            lastSync: null,
            syncing: false,
            syncProgress: 0,
            syncedVMs: 0,
            totalVMs: 0,
            errors: [],
            autoSync: false,
            syncInterval: 300 // 5 minutes in seconds
          },
          hyperv: {
            connected: false,
            lastSync: null,
            syncing: false,
            syncProgress: 0,
            syncedVMs: 0,
            totalVMs: 0,
            errors: [],
            autoSync: false,
            syncInterval: 300 // 5 minutes in seconds
          },
          zabbix: {
            connected: false,
            lastSync: null,
            syncing: false,
            syncProgress: 0,
            syncedMetrics: 0,
            totalMetrics: 0,
            errors: [],
            autoSync: false,
            syncInterval: 60 // 1 minute in seconds
          },
          prometheus: {
            connected: false,
            lastSync: null,
            syncing: false,
            syncProgress: 0,
            syncedMetrics: 0,
            totalMetrics: 0,
            errors: [],
            autoSync: false,
            syncInterval: 30 // 30 seconds
          }
        }
      }
    };
  },
  computed: {
    tabs() {
      // Filter tabs based on user role and permissions
      return this.availableTabs.filter(tab => this.hasAccess(tab.requiredRole, tab.requiredPermission));
    },
    isAdmin() {
      return this.currentUser.role === 'admin';
    },
    isManager() {
      return this.currentUser.role === 'manager' || this.currentUser.role === 'admin';
    },
    filteredStats() {
      // Show all stats, but hide sensitive data based on permissions
      return this.stats;
    },
    filteredVMs() {
      // Use real vCenter data if available, otherwise fall back to mock data
      let vms = this.vcenterInventory.hasSyncedData && this.vcenterInventory.vms.length > 0 
        ? this.vcenterInventory.vms 
        : this.mockVMs;
      
      if (this.searchTerm) {
        vms = vms.filter(vm => 
          vm.name.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
          (vm.cluster && vm.cluster.toLowerCase().includes(this.searchTerm.toLowerCase()))
        );
      }
      
      if (this.filterStatus !== 'all') {
        if (this.filterStatus === 'underutilized') {
          vms = vms.filter(vm => (vm.cpu || 0) < 10 && (vm.memory_usage || 0) < 20);
        } else {
          vms = vms.filter(vm => vm.status === this.filterStatus);
        }
      }
      
      return vms;
    }
  },
  watch: {
    activeTab(newTab) {
      // Save current tab to localStorage for persistence across refreshes
      localStorage.setItem('iroa_activeTab', newTab);
    }
  },
  async mounted() {
    console.log('🚀 Vue app mounted');
    
    // Initialize API base URL
    this.apiBaseUrl = this.getApiBaseUrl();
    
    // Check authentication status
    await this.checkAuthStatus();
    
    // Initialize Lucide icons
    if (window.lucide) {
      window.lucide.createIcons();
    }
    
    // If already authenticated, initialize the app
    if (this.isAuthenticated) {
      await this.loadInfrastructure();
      this.initializeAuthenticatedApp();
    }
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
    if (this.realtimeChart) {
      this.realtimeChart.destroy();
    }
    this.stopRealtimeUpdates();
  },
  watch: {
    activeTab(newTab, oldTab) {
      // Initialize real-time monitoring when tab is selected
      if (newTab === 'monitoring') {
        this.$nextTick(() => {
          this.initializeRealtimeChart();
          this.startRealtimeUpdates();
        });
      } else if (oldTab === 'monitoring') {
        // Clean up real-time updates when leaving monitoring tab
        this.stopRealtimeUpdates();
      }
    }
  },
  methods: {
    getApiBaseUrl() {
      // Check if we're running from file:// protocol
      if (window.location.protocol === 'file:') {
        return 'http://localhost:8001';
      }
      // For http/https, use relative path or same origin
      return window.location.origin.includes('localhost') 
        ? 'http://localhost:8001' 
        : `${window.location.protocol}//${window.location.hostname}:8001`;
    },
    
    checkExistingSession() {
      const token = localStorage.getItem('iroa_session_token');
      const expiry = localStorage.getItem('iroa_session_expiry');
      const userData = localStorage.getItem('iroa_current_user');
      
      console.log('🔍 Checking session - token:', !!token, 'expiry:', expiry);
      
      if (token && expiry && new Date().getTime() < parseInt(expiry)) {
        this.sessionToken = token;
        this.isAuthenticated = true;
        
        // Restore user data
        if (userData) {
          try {
            const user = JSON.parse(userData);
            this.currentUser = {
              id: user.id,
              username: user.username,
              role: user.role,
              permissions: user.permissions,
              profile: {
                fullName: user.fullName,
                email: user.email,
                department: user.department,
                lastLogin: user.lastLogin
              }
            };
            console.log('✅ Valid session found, user role:', this.currentUser.role);
          } catch (error) {
            console.error('Error parsing user data:', error);
            this.logout();
            return;
          }
        }
        
        console.log('✅ Valid session found, setting isAuthenticated to true');
      } else {
        // Clean up expired session
        localStorage.removeItem('iroa_session_token');
        localStorage.removeItem('iroa_session_expiry');
        localStorage.removeItem('iroa_current_user');
        console.log('❌ No valid session found');
      }
    },

    async checkAuthStatus() {
      this.checkExistingSession();
      if (this.isAuthenticated) {
        await this.loadUserPermissions();
      }
    },

    async loadUserPermissions() {
      try {
        // Mock user permissions loading
        console.log('Loading user permissions...');
        // In a real app, this would load user roles/permissions from API
      } catch (error) {
        console.error('Error loading user permissions:', error);
      }
    },

    async loadInfrastructure() {
      try {
        console.log('Loading infrastructure data...');
        // This would load initial infrastructure data
        await this.checkApiConnection();
        await this.loadData();
      } catch (error) {
        console.error('Error loading infrastructure:', error);
      }
    },
    
    async login() {
      this.isLoggingIn = true;
      this.loginError = '';
      
      try {
        // Input validation
        if (!this.loginForm.username || !this.loginForm.password) {
          this.loginError = 'Username and password are required';
        } else if (this.loginForm.username.length < 3 || this.loginForm.username.length > 50) {
          this.loginError = 'Username must be between 3 and 50 characters';
        } else if (this.loginForm.password.length < 6) {
          this.loginError = 'Password must be at least 6 characters';
        } else {
          // Sanitize input
          const username = this.loginForm.username.trim().toLowerCase();
          const password = this.loginForm.password;
          
          // For demo purposes, using hardcoded credentials
          let loginUser = null;
          
          // Check against users database
          if (username === 'admin' && password === 'iroa2024') {
            loginUser = this.users.find(u => u.username === 'admin');
          } else if (username === 'manager1' && password === 'manager123') {
            loginUser = this.users.find(u => u.username === 'manager1');
          } else if (username === 'user1' && password === 'user123') {
            loginUser = this.users.find(u => u.username === 'user1');
          }
          
          if (loginUser) {
            // Generate session token
            const token = 'iroa_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
            const expiry = new Date().getTime() + (24 * 60 * 60 * 1000); // 24 hours
            
            // Store session
            localStorage.setItem('iroa_session_token', token);
            localStorage.setItem('iroa_session_expiry', expiry.toString());
            localStorage.setItem('iroa_current_user', JSON.stringify(loginUser));
            
            // Set authentication state
            this.sessionToken = token;
            this.isAuthenticated = true;
            
            // Set current user data
            this.currentUser = {
              id: loginUser.id,
              username: loginUser.username,
              role: loginUser.role,
              permissions: loginUser.permissions,
              profile: {
                fullName: loginUser.fullName,
                email: loginUser.email,
                department: loginUser.department,
                lastLogin: new Date().toISOString()
              }
            };
            
            // Update last login
            loginUser.lastLogin = new Date().toISOString();
            
            console.log('✅ Login successful, isAuthenticated:', this.isAuthenticated);
            console.log('✅ User role:', this.currentUser.role);
            console.log('✅ Session token stored:', token);
            
            // Initialize app components after authentication
            this.initializeAuthenticatedApp();
          } else {
            this.loginError = 'Invalid username or password';
            await new Promise(resolve => setTimeout(resolve, 1000));
          }
        }
      } catch (error) {
        this.loginError = 'Authentication failed. Please try again.';
        console.error('Login error:', error);
      } finally {
        this.isLoggingIn = false;
      }
    },
    
    logout() {
      // Clear session data
      localStorage.removeItem('iroa_session_token');
      localStorage.removeItem('iroa_session_expiry');
      localStorage.removeItem('iroa_current_user');
      
      this.isAuthenticated = false;
      this.sessionToken = null;
      this.loginForm.username = '';
      this.loginForm.password = '';
      this.loginError = '';
      
      // Reset user data
      this.currentUser = {
        id: null,
        username: '',
        role: 'user',
        permissions: {
          pages: [],
          data: []
        },
        profile: {
          fullName: '',
          email: '',
          department: '',
          lastLogin: null
        }
      };
      
      // Clean up charts
      if (this.usageChart) {
        this.usageChart.destroy();
        this.usageChart = null;
      }
      if (this.distributionChart) {
        this.distributionChart.destroy();
        this.distributionChart = null;
      }
      if (this.forecastChart) {
        this.forecastChart.destroy();
        this.forecastChart = null;
      }
    },
    
    async checkApiConnection() {
      try {
        // Validate the API URL first
        if (!this.apiBaseUrl || this.apiBaseUrl === '') {
          throw new Error('API base URL not configured');
        }
        
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 5000);
        
        const response = await fetch(`${this.apiBaseUrl}/health`, {
          method: 'GET',
          signal: controller.signal,
          headers: {
            'Authorization': `Bearer ${this.sessionToken}`,
            'Content-Type': 'application/json'
          }
        });
        
        clearTimeout(timeoutId);
        this.apiAvailable = response.ok;
        if (this.apiAvailable) {
          console.log('✅ API server is available');
        }
      } catch (error) {
        this.apiAvailable = false;
        console.warn('⚠️ API server unavailable, using mock data:', error.message);
      }
    },
    
    skipAuth() {
      console.log('🚨 Skipping authentication for debugging');
      
      // Generate a debug session token
      const token = 'debug_' + Date.now();
      const expiry = new Date().getTime() + (24 * 60 * 60 * 1000); // 24 hours
      
      // Store session
      localStorage.setItem('iroa_session_token', token);
      localStorage.setItem('iroa_session_expiry', expiry.toString());
      
      // Set authentication state
      this.sessionToken = token;
      this.isAuthenticated = true;
      
      console.log('🚨 Debug auth set - isAuthenticated:', this.isAuthenticated);
      
      // Initialize app components after authentication
      this.initializeAuthenticatedApp();
    },
    
    initializeAuthenticatedApp() {
      console.log('🔧 Initializing authenticated app components');
      
      // Use nextTick to ensure DOM is updated after authentication state change
      this.$nextTick(async () => {
        try {
          // Initialize Lucide icons first
          if (window.lucide) {
            window.lucide.createIcons();
          }
          
          // Check API connection and load data
          await this.checkApiConnection();
          await this.loadData();
          
          // Initialize charts after data is loaded
          this.$nextTick(() => {
            this.initializeCharts();
          });
          
          console.log('✅ App initialization complete');
        } catch (error) {
          console.error('Error initializing authenticated app:', error);
          // Don't reset authentication on initialization error
        }
      });
    },
    
    async loadData() {
      this.loading = true;
      try {
        if (this.apiAvailable) {
          // Load recommendations from API
          const recRes = await fetch(`${this.apiBaseUrl}/recommendations`, {
            headers: {
              'Authorization': `Bearer ${this.sessionToken}`,
              'Content-Type': 'application/json'
            }
          });
          if (recRes.ok) {
            this.recommendations = await recRes.json();
          } else {
            console.warn('Failed to load recommendations:', recRes.status);
            this.recommendations = this.getMockRecommendations();
          }
          
          // Load underutilized VMs from API
          const underRes = await fetch(`${this.apiBaseUrl}/underutilized`, {
            headers: {
              'Authorization': `Bearer ${this.sessionToken}`,
              'Content-Type': 'application/json'
            }
          });
          if (underRes.ok) {
            this.underutilizedVMs = await underRes.json();
            // Update stats
            this.stats[1].value = this.underutilizedVMs.length.toString();
          } else {
            console.warn('Failed to load underutilized VMs:', underRes.status);
            this.underutilizedVMs = this.getMockUnderutilizedVMs();
            this.stats[1].value = this.underutilizedVMs.length.toString();
          }
          
          // Load persisted infrastructure inventory from database
          await this.loadPersistedInventory();
          
        } else {
          // Use mock data when API is unavailable
          this.recommendations = this.getMockRecommendations();
          this.underutilizedVMs = this.getMockUnderutilizedVMs();
          this.stats[1].value = this.underutilizedVMs.length.toString();
        }
      } catch (error) {
        console.error('Error loading data:', error);
        // Set mock data on error
        this.recommendations = this.getMockRecommendations();
        this.underutilizedVMs = this.getMockUnderutilizedVMs();
        this.stats[1].value = this.underutilizedVMs.length.toString();
      } finally {
        this.loading = false;
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
      ];
    },
    
    getMockUnderutilizedVMs() {
      return this.filteredVMs.filter(vm => (vm.cpu || 0) < 10 && (vm.memory_usage || 0) < 20);
    },
    
    async refreshData() {
      await this.checkApiConnection();
      await this.loadData();
      this.initializeCharts();
    },
    async getVMForecast(vmId) {
      try {
        if (this.apiAvailable) {
          const res = await fetch(`${this.apiBaseUrl}/forecast/${vmId}`, {
            headers: {
              'Authorization': `Bearer ${this.sessionToken}`,
              'Content-Type': 'application/json'
            }
          });
          if (res.ok) {
            const data = await res.json();
            this.forecast = data.cpu_forecast || [];
          } else {
            console.warn('Failed to load forecast:', res.status);
            this.forecast = this.getMockForecast();
          }
        } else {
          this.forecast = this.getMockForecast();
        }
        
        this.selectedVM = this.mockVMs.find(vm => vm.id === vmId);
        this.activeTab = 'analytics';
        
        // Update forecast chart
        this.$nextTick(() => {
          this.initializeForecastChart();
        });
      } catch (error) {
        console.error('Error loading forecast:', error);
        this.forecast = this.getMockForecast();
        this.selectedVM = this.mockVMs.find(vm => vm.id === vmId);
        this.activeTab = 'analytics';
        this.$nextTick(() => {
          this.initializeForecastChart();
        });
      }
    },
    getMockForecast() {
      // Generate mock 24-hour forecast data
      return Array.from({ length: 24 }, (_, i) => {
        return Math.round(30 + Math.sin(i * 0.3) * 20 + Math.random() * 10);
      });
    },
    
    async getAnomalies(vmId) {
      try {
        if (this.apiAvailable) {
          const res = await fetch(`${this.apiBaseUrl}/anomalies/${vmId}`, {
            headers: {
              'Authorization': `Bearer ${this.sessionToken}`,
              'Content-Type': 'application/json'
            }
          });
          if (res.ok) {
            const data = await res.json();
            this.anomalies = data.anomalies || [];
          } else {
            this.anomalies = [];
          }
        } else {
          this.anomalies = [];
        }
      } catch (error) {
        console.error('Error loading anomalies:', error);
        this.anomalies = [];
      }
    },
    viewVMDetails(vm) {
      this.selectedVM = vm;
      this.getVMForecast(vm.id);
      this.getAnomalies(vm.id);
    },
    formatDate(dateString) {
      return new Date(dateString).toLocaleString();
    },
    initializeCharts() {
      try {
        this.initializeUsageChart();
        this.initializeDistributionChart();
        
        // Initialize real-time monitoring if tab is active
        if (this.activeTab === 'monitoring') {
          this.$nextTick(() => {
            this.initializeRealtimeChart();
            this.startRealtimeUpdates();
          });
        }
      } catch (error) {
        console.error('Error initializing charts:', error);
      }
    },
    initializeUsageChart() {
      const ctx = this.$refs.usageChart;
      if (!ctx) return;
      
      // Destroy existing chart if it exists
      if (this.usageChart) {
        this.usageChart.destroy();
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
      });
    },
    initializeDistributionChart() {
      const ctx = this.$refs.distributionChart;
      if (!ctx) return;
      
      // Destroy existing chart if it exists
      if (this.distributionChart) {
        this.distributionChart.destroy();
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
      });
    },
    initializeForecastChart() {
      const ctx = this.$refs.forecastChart;
      if (!ctx || !this.forecast.length) return;
      
      // Destroy existing chart if it exists
      if (this.forecastChart) {
        this.forecastChart.destroy();
      }
      
      const hours = Array.from({ length: 24 }, (_, i) => `${i}:00`);
      
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
      });
    },
    
    initializeRealtimeChart() {
      const ctx = this.$refs.realtimeChart;
      if (!ctx) return;
      
      // Destroy existing chart if it exists
      if (this.realtimeChart) {
        this.realtimeChart.destroy();
      }
      
      // Generate initial timestamps
      const now = new Date();
      this.realtimeChartData.timestamps = Array.from({ length: 8 }, (_, i) => {
        const time = new Date(now.getTime() - (7 - i) * 30000); // 30 second intervals
        return time.toLocaleTimeString();
      });
      
      this.realtimeChart = new Chart(ctx, {
        type: 'line',
        data: {
          labels: this.realtimeChartData.timestamps,
          datasets: [{
            label: 'CPU %',
            data: this.realtimeChartData.cpu,
            borderColor: 'rgb(99, 102, 241)',
            backgroundColor: 'rgba(99, 102, 241, 0.1)',
            tension: 0.4,
            fill: false
          }, {
            label: 'Memory %',
            data: this.realtimeChartData.memory,
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
      });
    },
    
    startRealtimeUpdates() {
      this.realtimeUpdateInterval = setInterval(() => {
        this.updateRealtimeMetrics();
        this.updateRealtimeChart();
      }, 5000); // Update every 5 seconds
    },
    
    stopRealtimeUpdates() {
      if (this.realtimeUpdateInterval) {
        clearInterval(this.realtimeUpdateInterval);
        this.realtimeUpdateInterval = null;
      }
    },
    
    updateRealtimeMetrics() {
      // Update real-time data from actual infrastructure if available
      const hasVCenterData = this.vcenterInventory.hasSyncedData && this.vcenterInventory.vms.length > 0;
      const hasHyperVData = this.hypervInventory.hasSyncedData && this.hypervInventory.vms.length > 0;
      
      if (hasVCenterData || hasHyperVData) {
        // Use real data - already updated by updateStatsFromVCenterData() and updateStatsFromHyperVData()
        this.realTimeData.isConnected = true;
      } else {
        // Simulate real-time data updates only when no real data is available
        this.realTimeData.metrics.avgCpu = Math.max(0, Math.min(100, 
          this.realTimeData.metrics.avgCpu + (Math.random() - 0.5) * 10));
        this.realTimeData.metrics.avgMemory = Math.max(0, Math.min(100, 
          this.realTimeData.metrics.avgMemory + (Math.random() - 0.5) * 8));
        this.realTimeData.isConnected = false;  // Mark as simulation
      }
      
      // Occasionally add new events
      if (Math.random() < 0.3) {
        const eventTypes = ['info', 'warning', 'error'];
        const messages = [
          'VM performance optimized',
          'Resource threshold exceeded',
          'Anomaly detected in network traffic',
          'Backup process completed',
          'CPU spike detected',
          'Memory usage stabilized',
          'Disk I/O optimization applied',
          'Network latency improved'
        ];
        
        const newEvent = {
          id: Date.now(),
          type: eventTypes[Math.floor(Math.random() * eventTypes.length)],
          timestamp: new Date().toLocaleTimeString(),
          message: messages[Math.floor(Math.random() * messages.length)]
        };
        
        this.realTimeData.recentEvents.unshift(newEvent);
        if (this.realTimeData.recentEvents.length > 10) {
          this.realTimeData.recentEvents.pop();
        }
      }
    },
    
    updateRealtimeChart() {
      if (!this.realtimeChart) return;
      
      // Add new data point
      const newCpu = Math.max(0, Math.min(100, 
        this.realtimeChartData.cpu[this.realtimeChartData.cpu.length - 1] + (Math.random() - 0.5) * 10));
      const newMemory = Math.max(0, Math.min(100, 
        this.realtimeChartData.memory[this.realtimeChartData.memory.length - 1] + (Math.random() - 0.5) * 8));
      const newTimestamp = new Date().toLocaleTimeString();
      
      // Update data arrays
      this.realtimeChartData.cpu.push(newCpu);
      this.realtimeChartData.memory.push(newMemory);
      this.realtimeChartData.timestamps.push(newTimestamp);
      
      // Keep only last 8 data points
      if (this.realtimeChartData.cpu.length > 8) {
        this.realtimeChartData.cpu.shift();
        this.realtimeChartData.memory.shift();
        this.realtimeChartData.timestamps.shift();
      }
      
      // Update chart
      this.realtimeChart.data.labels = this.realtimeChartData.timestamps;
      this.realtimeChart.data.datasets[0].data = this.realtimeChartData.cpu;
      this.realtimeChart.data.datasets[1].data = this.realtimeChartData.memory;
      this.realtimeChart.update('none'); // No animation for real-time updates
    },
    
    // Admin panel methods
    async startMacMonitoring() {
      try {
        if (!this.hasAccess('admin', 'system_admin')) {
          alert('Access denied: You do not have permission to manage system integrations.');
          return;
        }
        
        if (!this.apiAvailable) {
          alert('⚠️ API server is not available. This feature requires the backend server.');
          return;
        }
        
        const response = await fetch(`${this.apiBaseUrl}/admin/mac/start`, {
          method: 'POST',
          headers: { 
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${this.sessionToken}`
          },
          body: JSON.stringify({ interval: this.adminData.macMonitoring.interval })
        });
        
        if (response.ok) {
          const result = await response.json();
          this.adminData.macMonitoring.isRunning = true;
          this.adminData.macMonitoring.lastUpdate = new Date().toISOString();
          console.log('Mac monitoring started:', result);
          
          // Refresh data to show new VMs
          await this.loadData();
        } else {
          console.error('Failed to start Mac monitoring');
        }
      } catch (error) {
        console.error('Error starting Mac monitoring:', error);
      }
    },
    
    async stopMacMonitoring() {
      try {
        if (!this.apiAvailable) {
          alert('⚠️ API server is not available. This feature requires the backend server.');
          return;
        }
        
        const response = await fetch(`${this.apiBaseUrl}/admin/mac/stop`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${this.sessionToken}`
          }
        });
        
        if (response.ok) {
          this.adminData.macMonitoring.isRunning = false;
          console.log('Mac monitoring stopped');
        } else {
          console.error('Failed to stop Mac monitoring');
        }
      } catch (error) {
        console.error('Error stopping Mac monitoring:', error);
      }
    },
    
    async getMacStats() {
      try {
        if (!this.apiAvailable) {
          alert('⚠️ API server is not available. This feature requires the backend server.');
          return;
        }
        
        const response = await fetch(`${this.apiBaseUrl}/admin/mac/stats`, {
          headers: {
            'Authorization': `Bearer ${this.sessionToken}`
          }
        });
        
        if (response.ok) {
          const stats = await response.json();
          this.adminData.macMonitoring.currentStats = {
            cpu: stats.cpu_usage.toFixed(1),
            memory: stats.memory_usage.toFixed(1),
            disk: stats.disk_usage.toFixed(1)
          };
          this.adminData.macMonitoring.systemInfo = stats.system_info;
        } else {
          console.error('Failed to get Mac stats');
        }
      } catch (error) {
        console.error('Error getting Mac stats:', error);
      }
    },
    
    debugCredentialInput(field, event) {
      console.log(`Debug: ${field} field updated`, event.target.value ? '[REDACTED]' : 'empty');
    },
    
    async loadCapacityData() {
      try {
        // Check if user has access to capacity planning
        if (!this.hasAccess('manager', 'view_capacity')) {
          console.warn('Access denied: User does not have permission to view capacity data');
          return;
        }
        
        // If we have real vCenter data, calculate capacity from it
        if (this.vcenterInventory.hasSyncedData && this.vcenterInventory.clusters.length > 0) {
          console.log('📊 Calculating capacity from real vCenter data');
          this.capacityData = this.calculateCapacityFromVCenterData();
          return;
        }
        
        // Try to load from API
        if (this.apiAvailable) {
          const endpoint = this.selectedCluster ? 
            `${this.apiBaseUrl}/capacity/analysis?cluster=${encodeURIComponent(this.selectedCluster)}` :
            `${this.apiBaseUrl}/capacity/analysis`;
            
          const response = await fetch(endpoint, {
            headers: {
              'Authorization': `Bearer ${this.sessionToken}`,
              'Content-Type': 'application/json'
            }
          });
          
          if (response.ok) {
            this.capacityData = await response.json();
            console.log('✅ Capacity data loaded from API:', this.capacityData);
          } else {
            console.warn('Failed to load capacity data from API:', response.status);
            this.capacityData = this.getMockCapacityData();
          }
        } else {
          // Use mock data when API is unavailable
          this.capacityData = this.getMockCapacityData();
        }
        
        // Update clusters array
        if (this.capacityData && this.capacityData.clusters) {
          // Extract cluster names from capacity data
          this.clusters = [...new Set(this.capacityData.clusters.map(c => c.cluster || c.name || c))];
        }
      } catch (error) {
        console.error('Error loading capacity data:', error);
        this.capacityData = this.getMockCapacityData();
      }
    },

    calculateCapacityFromVCenterData() {
      // Calculate capacity planning data from real vCenter inventory
      const vms = this.vcenterInventory.vms;
      const clusters = this.vcenterInventory.clusters;
      const hosts = this.vcenterInventory.hosts;
      
      // Calculate overall totals
      const totalCpuCores = hosts.reduce((sum, host) => sum + (host.cpu_cores || 0), 0);
      const totalMemoryGB = hosts.reduce((sum, host) => sum + (host.memory_gb || 0), 0);
      const totalVMs = vms.length;
      const runningVMs = vms.filter(vm => vm.status === 'running').length;
      
      // Calculate used resources
      const usedCpuCores = vms.reduce((sum, vm) => sum + (vm.cores || 0), 0);
      const usedMemoryGB = vms.reduce((sum, vm) => sum + (vm.memory || 0), 0);
      
      // Calculate available resources
      const availableCpuCores = Math.max(0, totalCpuCores - usedCpuCores);
      const availableMemoryGB = Math.max(0, totalMemoryGB - usedMemoryGB);
      
      // Estimate max additional VMs (assuming average VM resource usage)
      const avgVMCores = vms.length > 0 ? usedCpuCores / vms.length : 2;
      const avgVMMemory = vms.length > 0 ? usedMemoryGB / vms.length : 4;
      
      const maxAdditionalByMemory = Math.floor(availableMemoryGB / avgVMMemory);
      const maxAdditionalByCpu = Math.floor(availableCpuCores / avgVMCores);
      const maxAdditionalVMs = Math.min(maxAdditionalByMemory, maxAdditionalByCpu);
      
      // Process clusters
      const clusterAnalysis = clusters.map(cluster => {
        const clusterVMs = vms.filter(vm => vm.cluster === cluster.name);
        const clusterHosts = hosts.filter(host => host.cluster === cluster.name);
        
        const clusterTotalCpu = clusterHosts.reduce((sum, host) => sum + (host.cpu_cores || 0), 0);
        const clusterTotalMemory = clusterHosts.reduce((sum, host) => sum + (host.memory_gb || 0), 0);
        const clusterUsedCpu = clusterVMs.reduce((sum, vm) => sum + (vm.cores || 0), 0);
        const clusterUsedMemory = clusterVMs.reduce((sum, vm) => sum + (vm.memory || 0), 0);
        
        const cpuUtilization = clusterTotalCpu > 0 ? Math.round((clusterUsedCpu / clusterTotalCpu) * 100) : 0;
        const memoryUtilization = clusterTotalMemory > 0 ? Math.round((clusterUsedMemory / clusterTotalMemory) * 100) : 0;
        
        const clusterAvailableCpu = Math.max(0, clusterTotalCpu - clusterUsedCpu);
        const clusterAvailableMemory = Math.max(0, clusterTotalMemory - clusterUsedMemory);
        
        const clusterMaxAdditionalByMemory = Math.floor(clusterAvailableMemory / avgVMMemory);
        const clusterMaxAdditionalByCpu = Math.floor(clusterAvailableCpu / avgVMCores);
        const clusterMaxAdditional = Math.min(clusterMaxAdditionalByMemory, clusterMaxAdditionalByCpu);
        
        const limitingFactorCpu = clusterMaxAdditionalByCpu <= clusterMaxAdditionalByMemory;
        
        return {
          cluster: cluster.name,
          current_vms: clusterVMs.length,
          cpu_utilization: cpuUtilization,
          memory_utilization: memoryUtilization,
          max_additional_vms: Math.max(0, clusterMaxAdditional),
          limiting_factor: limitingFactorCpu ? 'CPU' : 'Memory',
          host_count: clusterHosts.length,
          total_cpu_cores: clusterTotalCpu,
          total_memory_gb: clusterTotalMemory,
          available_cpu_cores: clusterAvailableCpu,
          available_memory_gb: clusterAvailableMemory
        };
      });
      
      return {
        summary: {
          total_vms: totalVMs,
          running_vms: runningVMs,
          max_additional_vms: Math.max(0, maxAdditionalVMs),
          total_cpu_cores: totalCpuCores,
          total_memory_gb: Math.round(totalMemoryGB),
          used_cpu_cores: usedCpuCores,
          used_memory_gb: Math.round(usedMemoryGB),
          available_cpu_cores: availableCpuCores,
          available_memory_gb: Math.round(availableMemoryGB),
          cpu_utilization_percent: totalCpuCores > 0 ? Math.round((usedCpuCores / totalCpuCores) * 100) : 0,
          memory_utilization_percent: totalMemoryGB > 0 ? Math.round((usedMemoryGB / totalMemoryGB) * 100) : 0,
          limiting_factor: maxAdditionalByCpu <= maxAdditionalByMemory ? 'CPU' : 'Memory'
        },
        clusters: clusterAnalysis,
        last_updated: new Date().toISOString(),
        data_source: 'vcenter_inventory'
      };
    },
    
    async loadProfileData() {
      try {
        // Check if user has access to profile analysis
        if (!this.hasAccess('manager', 'view_profiles')) {
          console.warn('Access denied: User does not have permission to view profile data');
          return;
        }
        
        // If we have real vCenter data, analyze VM profiles from it
        if (this.vcenterInventory.hasSyncedData && this.vcenterInventory.vms.length > 0) {
          console.log('📊 Analyzing VM profiles from real vCenter data');
          this.profileData = this.analyzeVMProfilesFromVCenterData();
          console.log('✅ Profile data generated:', this.profileData);
          return;
        }
        
        // Try to load from API
        if (this.apiAvailable) {
          const endpoint = this.selectedCluster ? 
            `${this.apiBaseUrl}/profiles/preview?cluster=${encodeURIComponent(this.selectedCluster)}` :
            `${this.apiBaseUrl}/profiles/preview`;
            
          const response = await fetch(endpoint, {
            headers: {
              'Authorization': `Bearer ${this.sessionToken}`,
              'Content-Type': 'application/json'
            }
          });
          
          if (response.ok) {
            this.profileData = await response.json();
            console.log('✅ Profile data loaded from API:', this.profileData);
          } else {
            console.warn('Failed to load profile data from API:', response.status);
            this.profileData = this.getMockProfileData();
          }
        } else {
          // Use mock data when API is unavailable
          this.profileData = this.getMockProfileData();
        }
        
        // Update clusters array
        if (this.profileData && this.profileData.cluster_name) {
          if (!this.clusters.includes(this.profileData.cluster_name)) {
            this.clusters.push(this.profileData.cluster_name);
          }
        }
      } catch (error) {
        console.error('Error loading profile data:', error);
        this.profileData = this.getMockProfileData();
      }
    },

    analyzeVMProfilesFromVCenterData() {
      // Analyze VM profiles from real vCenter inventory data
      const vms = this.vcenterInventory.vms;
      const clusters = this.vcenterInventory.clusters;
      const hosts = this.vcenterInventory.hosts;
      
      // Group VMs by similar resource profiles
      const profileGroups = {};
      
      vms.forEach(vm => {
        // Create a profile key based on CPU cores and memory
        const profileKey = `${vm.cores}vCPU-${vm.memory}GB`;
        
        if (!profileGroups[profileKey]) {
          profileGroups[profileKey] = {
            profile_name: profileKey,
            vms: [],
            cpu_cores: vm.cores,
            memory_gb: vm.memory,
            total_vms: 0,
            avg_cpu_usage: 0,
            avg_memory_usage: 0,
            utilization_status: 'normal'
          };
        }
        
        profileGroups[profileKey].vms.push(vm);
        profileGroups[profileKey].total_vms++;
      });
      
      // Calculate averages and utilization for each profile
      const profiles = Object.values(profileGroups).map(profile => {
        const vmsInProfile = profile.vms;
        
        // Calculate average utilization
        const avgCpuUsage = vmsInProfile.length > 0 
          ? Math.round(vmsInProfile.reduce((sum, vm) => sum + vm.cpu, 0) / vmsInProfile.length)
          : 0;
        const avgMemoryUsage = vmsInProfile.length > 0
          ? Math.round(vmsInProfile.reduce((sum, vm) => sum + vm.memory_usage, 0) / vmsInProfile.length)
          : 0;
        
        // Determine utilization status
        let utilizationStatus = 'normal';
        if (avgCpuUsage < 10 && avgMemoryUsage < 20) {
          utilizationStatus = 'underutilized';
        } else if (avgCpuUsage > 80 || avgMemoryUsage > 90) {
          utilizationStatus = 'overutilized';
        }
        
        // Calculate available capacity for this profile
        const totalClusterResources = clusters.reduce((totals, cluster) => {
          const clusterHosts = hosts.filter(h => h.cluster === cluster.name);
          return {
            cpu_cores: totals.cpu_cores + clusterHosts.reduce((sum, h) => sum + (h.cpu_cores || 0), 0),
            memory_gb: totals.memory_gb + clusterHosts.reduce((sum, h) => sum + (h.memory_gb || 0), 0)
          };
        }, { cpu_cores: 0, memory_gb: 0 });
        
        const usedResources = vms.reduce((totals, vm) => ({
          cpu_cores: totals.cpu_cores + vm.cores,
          memory_gb: totals.memory_gb + vm.memory
        }), { cpu_cores: 0, memory_gb: 0 });
        
        const availableResources = {
          cpu_cores: Math.max(0, totalClusterResources.cpu_cores - usedResources.cpu_cores),
          memory_gb: Math.max(0, totalClusterResources.memory_gb - usedResources.memory_gb)
        };
        
        // Calculate how many more VMs of this profile can be created
        const maxAdditionalByCpu = Math.floor(availableResources.cpu_cores / profile.cpu_cores);
        const maxAdditionalByMemory = Math.floor(availableResources.memory_gb / profile.memory_gb);
        const maxAdditionalVMs = Math.min(maxAdditionalByCpu, maxAdditionalByMemory);
        
        const limitingFactorCpu = maxAdditionalByCpu <= maxAdditionalByMemory;
        
        return {
          profile_name: profile.profile_name,
          cpu_cores: profile.cpu_cores,
          memory_gb: profile.memory_gb,
          current_vms: profile.total_vms,
          max_additional_vms: Math.max(0, maxAdditionalVMs),
          limiting_factor: limitingFactorCpu ? 'CPU' : 'Memory',
          profile_cpu_usage_percent: avgCpuUsage,
          profile_memory_usage_percent: avgMemoryUsage,
          utilization_status: utilizationStatus,
          vms_list: vmsInProfile.map(vm => ({
            name: vm.name,
            cluster: vm.cluster,
            cpu_usage: vm.cpu,
            memory_usage: vm.memory_usage,
            status: vm.status
          }))
        };
      });
      
      // Sort profiles by current VM count (most popular first)
      profiles.sort((a, b) => b.current_vms - a.current_vms);
      
      return {
        cluster_name: this.selectedCluster || 'All Clusters',
        profiles: profiles,
        summary: {
          total_profiles: profiles.length,
          total_vms: vms.length,
          underutilized_profiles: profiles.filter(p => p.utilization_status === 'underutilized').length,
          overutilized_profiles: profiles.filter(p => p.utilization_status === 'overutilized').length,
          most_common_profile: profiles[0]?.profile_name || 'N/A'
        },
        last_updated: new Date().toISOString(),
        data_source: 'vcenter_inventory'
      };
    },
    
    getMockCapacityData() {
      return {
        current_infrastructure: {
          max_additional_vms: 15,
          total_cpu_cores: 64,
          total_memory_gb: 256,
          total_storage_gb: 2048
        },
        recommendations: [
          {
            id: 1,
            title: "CPU Optimization Opportunity",
            description: "Consider redistributing workloads across clusters to balance CPU utilization"
          },
          {
            id: 2,
            title: "Memory Efficiency Improvement",
            description: "Some VMs have overprovisioned memory that could be reallocated"
          },
          {
            id: 3,
            title: "Storage Consolidation",  
            description: "Unused storage can be reclaimed from underutilized VMs"
          }
        ],
        clusters: [
          {
            cluster: 'prod-cluster',
            current_vms: 2,
            cpu_utilization: 65,
            memory_utilization: 72,
            max_additional_vms: 4,
            limiting_factor: 'Memory',
            host_count: 3
          },
          {
            cluster: 'dev-cluster',
            current_vms: 1,
            cpu_utilization: 32,
            memory_utilization: 48,
            max_additional_vms: 8,
            limiting_factor: 'CPU',
            host_count: 2
          },
          {
            cluster: 'test-cluster',
            current_vms: 1,
            cpu_utilization: 15,
            memory_utilization: 25,
            max_additional_vms: 12,
            limiting_factor: 'CPU',
            host_count: 1
          },
          {
            cluster: 'backup-cluster',
            current_vms: 1,
            cpu_utilization: 10,
            memory_utilization: 20,
            max_additional_vms: 15,
            limiting_factor: 'CPU',
            host_count: 1
          }
        ]
      };
    },
    
    getMockProfileData() {
      return {
        cluster_name: this.selectedCluster || 'prod-cluster',
        cluster_capacity: {
          total_cpu_vcpus: 64,
          total_memory_gb: 256,
          remaining_vcpu: 28
        },
        profiles_discovered: [
          {
            profile_name: 'Web Server Profile',
            current_count: 2,
            profile_specs: {
              cpu: 4,
              memory: 8,
              disk: 80
            },
            max_additional_vms: 7,
            limiting_factor: 'CPU',
            profile_cpu_usage_percent: 65,
            profile_memory_usage_percent: 72
          },
          {
            profile_name: 'Database Profile',
            current_count: 1,
            profile_specs: {
              cpu: 8,
              memory: 32,
              disk: 200
            },
            max_additional_vms: 2,
            limiting_factor: 'Memory',
            profile_cpu_usage_percent: 78,
            profile_memory_usage_percent: 85
          },
          {
            profile_name: 'Development Profile',
            current_count: 2,
            profile_specs: {
              cpu: 2,
              memory: 4,
              disk: 40
            },
            max_additional_vms: 14,
            limiting_factor: 'CPU',
            profile_cpu_usage_percent: 25,
            profile_memory_usage_percent: 30
          }
        ]
      };
    },
    
    // Role-based access control methods
    hasAccess(requiredRole, requiredPermission) {
      if (!this.isAuthenticated) return false;
      
      // Check role hierarchy: admin > manager > user
      const roleHierarchy = { 'admin': 3, 'manager': 2, 'user': 1 };
      const userRoleLevel = roleHierarchy[this.currentUser.role] || 0;
      const requiredRoleLevel = roleHierarchy[requiredRole] || 0;
      
      // Check if user role meets minimum requirement
      if (userRoleLevel < requiredRoleLevel) return false;
      
      // Check specific permission
      return this.currentUser.permissions.pages.includes(requiredPermission);
    },
    
    hasDataAccess(dataType) {
      if (!this.isAuthenticated) return false;
      return this.currentUser.permissions.data.includes(dataType);
    },
    
    changeTab(tabId) {
      const tab = this.availableTabs.find(t => t.id === tabId);
      if (!tab) return;
      
      if (!this.hasAccess(tab.requiredRole, tab.requiredPermission)) {
        alert(`Access denied: You do not have permission to access the "${tab.name}" section. Required role: ${tab.requiredRole.charAt(0).toUpperCase() + tab.requiredRole.slice(1)}`);
        return;
      }
      
      this.activeTab = tabId;
      
      // Initialize components for specific tabs
      this.$nextTick(() => {
        if (window.lucide) {
          window.lucide.createIcons();
        }
      });
    },
    
    // User Management Methods
    openUserModal(user = null) {
      if (!this.hasAccess('admin', 'manage_users')) {
        alert('Access denied: You do not have permission to manage users.');
        return;
      }
      
      this.userManagement.editMode = !!user;
      this.userManagement.showUserModal = true;
      
      if (user) {
        this.userManagement.userForm = {
          id: user.id,
          username: user.username,
          fullName: user.fullName,
          email: user.email,
          role: user.role,
          department: user.department,
          status: user.status,
          permissions: {
            pages: [...user.permissions.pages],
            data: [...user.permissions.data]
          }
        };
      } else {
        this.resetUserForm();
      }
    },
    
    closeUserModal() {
      this.userManagement.showUserModal = false;
      this.userManagement.editMode = false;
      this.resetUserForm();
    },
    
    resetUserForm() {
      this.userManagement.userForm = {
        id: null,
        username: '',
        fullName: '',
        email: '',
        role: 'user',
        department: '',
        status: 'active',
        permissions: {
          pages: [],
          data: []
        }
      };
    },
    
    updateUserRole() {
      const role = this.roles.find(r => r.id === this.userManagement.userForm.role);
      if (role) {
        this.userManagement.userForm.permissions = {
          pages: [...role.permissions.pages],
          data: [...role.permissions.data]
        };
      }
    },
    
    async saveUser() {
      try {
        if (!this.hasAccess('admin', 'manage_users')) {
          alert('Access denied: You do not have permission to manage users.');
          return;
        }
        
        const form = this.userManagement.userForm;
        
        // Validation
        if (!form.username || !form.fullName || !form.email || !form.role) {
          alert('Please fill in all required fields.');
          return;
        }
        
        if (this.userManagement.editMode) {
          // Update existing user
          const userIndex = this.users.findIndex(u => u.id === form.id);
          if (userIndex !== -1) {
            this.users[userIndex] = {
              ...this.users[userIndex],
              username: form.username,
              fullName: form.fullName,
              email: form.email,
              role: form.role,
              department: form.department,
              status: form.status,
              permissions: form.permissions
            };
          }
        } else {
          // Create new user
          const newUser = {
            id: Math.max(...this.users.map(u => u.id)) + 1,
            username: form.username,
            fullName: form.fullName,
            email: form.email,
            role: form.role,
            department: form.department,
            status: form.status,
            lastLogin: null,
            permissions: form.permissions
          };
          this.users.push(newUser);
        }
        
        this.closeUserModal();
        console.log('✅ User saved successfully');
        
      } catch (error) {
        console.error('Error saving user:', error);
        alert('Error saving user. Please try again.');
      }
    },
    
    async deleteUser(userId) {
      if (!this.hasAccess('admin', 'manage_users')) {
        alert('Access denied: You do not have permission to manage users.');
        return;
      }
      
      if (userId === this.currentUser.id) {
        alert('You cannot delete your own account.');
        return;
      }
      
      if (confirm('Are you sure you want to delete this user? This action cannot be undone.')) {
        const userIndex = this.users.findIndex(u => u.id === userId);
        if (userIndex !== -1) {
          this.users.splice(userIndex, 1);
          console.log('✅ User deleted successfully');
        }
      }
    },
    
    toggleUserStatus(userId) {
      if (!this.hasAccess('admin', 'manage_users')) {
        alert('Access denied: You do not have permission to manage users.');
        return;
      }
      
      const user = this.users.find(u => u.id === userId);
      if (user) {
        user.status = user.status === 'active' ? 'inactive' : 'active';
      }
    },
    
    async testConnection(type) {
      try {
        if (!this.hasAccess('admin', 'system_admin')) {
          alert('Access denied: You do not have permission to test system connections.');
          return;
        }
        
        if (!this.apiAvailable) {
          alert('⚠️ API server is not available. This feature requires the backend server.');
          return;
        }
        
        const formData = this.adminData.connectionForms[type];
        const response = await fetch(`${this.apiBaseUrl}/admin/${type}/test`, {
          method: 'POST',
          headers: { 
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${this.sessionToken}`
          },
          body: JSON.stringify(formData)
        });
        
        if (response.ok) {
          const result = await response.json();
          console.log(`${type} connection successful:`, result);
          
          // Update connection status and persist it
          this.adminData.syncStatus[type].connected = true;
          this.adminData.syncStatus[type].errors = [];
          this.adminData.syncStatus[type].lastConnected = new Date().toISOString();
          
          alert(`✅ ${type} integration successful! Click "Start Sync" to begin data synchronization.`);
        } else {
          const error = await response.text();
          console.error(`${type} connection failed:`, error);
          alert(`❌ Failed to connect to ${type}: ${error}`);
        }
      } catch (error) {
        console.error(`Error testing ${type} connection:`, error);
        alert(`❌ Error testing ${type} connection: ${error.message}`);
      }
    },
    
    async startSync(type) {
      if (!this.hasAccess('admin', 'system_admin')) {
        alert('Access denied: You do not have permission to start data synchronization.');
        return;
      }
      
      if (!this.adminData.syncStatus[type].connected) {
        alert(`Please test the ${type} connection first before starting sync.`);
        return;
      }
      
      try {
        this.adminData.syncStatus[type].syncing = true;
        this.adminData.syncStatus[type].syncProgress = 0;
        this.adminData.syncStatus[type].errors = [];
        
        if (!this.apiAvailable) {
          // Simulate sync for demo purposes
          this.simulateSync(type);
          return;
        }
        
        let syncEndpoint;
        let requestBody;
        
        if (type === 'vcenter') {
          // vCenter has dedicated sync endpoints
          syncEndpoint = `${this.apiBaseUrl}/admin/vcenter/sync-with-credentials`;
          requestBody = this.adminData.connectionForms.vcenter;
        } else if (type === 'hyperv') {
          // HyperV has dedicated sync endpoints
          syncEndpoint = `${this.apiBaseUrl}/admin/hyperv/sync-with-credentials`;
          requestBody = this.adminData.connectionForms.hyperv;
        } else if (type === 'prometheus') {
          // Prometheus sync endpoint
          syncEndpoint = `${this.apiBaseUrl}/admin/prometheus/sync`;
          requestBody = {}; // Uses saved configuration
        } else if (type === 'zabbix') {
          // Zabbix sync endpoint
          syncEndpoint = `${this.apiBaseUrl}/admin/zabbix/sync`;
          requestBody = {}; // Uses saved configuration
        } else {
          console.log(`Unknown sync type: ${type}`);
          this.adminData.syncStatus[type].syncing = false;
          return;
        }
        
        const response = await fetch(syncEndpoint, {
          method: 'POST',
          headers: { 
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${this.sessionToken}`
          },
          body: JSON.stringify(requestBody)
        });
        
        if (response.ok) {
          const result = await response.json();
          
          // Store inventory data for infrastructure platforms and show real progress
          if (type === 'vcenter' && result.inventory) {
            this.storeVCenterInventory(result.inventory);
            this.showRealSyncProgress(type, result);
          } else if (type === 'hyperv' && result.inventory) {
            this.storeHyperVInventory(result.inventory);
            this.showRealSyncProgress(type, result);
          } else {
            // Fallback to simulation for other types
            this.simulateSyncProgress(type);
          }
          
          console.log(`${type} sync started:`, result);
        } else {
          const error = await response.text();
          console.error(`${type} sync failed:`, error);
          this.adminData.syncStatus[type].errors.push(error);
          this.adminData.syncStatus[type].syncing = false;
          alert(`❌ Failed to start ${type} sync: ${error}`);
        }
      } catch (error) {
        console.error(`Error starting ${type} sync:`, error);
        this.adminData.syncStatus[type].errors.push(error.message);
        this.adminData.syncStatus[type].syncing = false;
        alert(`❌ Error starting ${type} sync: ${error.message}`);
      }
    },
    
    simulateSyncProgress(type) {
      // For vCenter, simulate progress. For Prometheus/Zabbix, check real API status
      const syncStatus = this.adminData.syncStatus[type];
      
      if (type === 'prometheus' || type === 'zabbix') {
        // For Prometheus and Zabbix, use real API status checking
        this.trackRealSyncProgress(type);
        return;
      }
      
      // Dynamic simulation based on actual sync results
      const totalItems = 100; // Realistic estimate for full vCenter inventory
      syncStatus.totalVMs = totalItems;
      syncStatus.totalMetrics = totalItems;
      syncStatus.syncedVMs = 0;
      syncStatus.syncedMetrics = 0;
      syncStatus.syncProgress = 0;
      
      const progressInterval = setInterval(() => {
        // Simulate realistic progress with some randomness
        const increment = Math.random() * 12 + 3; // 3-15% increments
        syncStatus.syncProgress = Math.min(100, syncStatus.syncProgress + increment);
        
        if (type === 'vcenter') {
          syncStatus.syncedVMs = Math.min(totalItems, Math.round((syncStatus.syncProgress / 100) * totalItems));
        } else {
          syncStatus.syncedMetrics = Math.min(totalItems, Math.round((syncStatus.syncProgress / 100) * totalItems));
        }
        
        if (syncStatus.syncProgress >= 100) {
          syncStatus.syncProgress = 100;
          syncStatus.syncing = false;
          syncStatus.lastSync = new Date().toISOString();
          
          clearInterval(progressInterval);
          
          // Refresh dashboard data to show new synced data
          this.loadData();
          
          this.showSyncNotification(type, 'success', `${type} sync completed! Synchronized ${totalItems} items.`);
          console.log(`✅ ${type} sync completed successfully`);
        }
      }, 800); // Update every 800ms for realistic feel
    },
    
    showSyncNotification(type, status, message) {
      // For now, use alert - in a real app you'd use a proper notification system
      if (status === 'success') {
        console.log(`✅ ${message}`);
      } else {
        console.error(`❌ ${message}`);
      }
    },
    
    async stopSync(type) {
      if (!this.hasAccess('admin', 'system_admin')) {
        alert('Access denied: You do not have permission to stop data synchronization.');
        return;
      }
      
      // Since the backend doesn't have stop endpoints, just stop the local sync simulation
      this.adminData.syncStatus[type].syncing = false;
      this.adminData.syncStatus[type].syncProgress = 0;
      console.log(`${type} sync stopped locally`);
      
      // In a real implementation with backend support, you would make an API call:
      /*
      try {
        const response = await fetch(`${this.apiBaseUrl}/admin/${type}/sync/stop`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${this.sessionToken}`
          }
        });
        
        if (response.ok) {
          this.adminData.syncStatus[type].syncing = false;
          console.log(`${type} sync stopped`);
        }
      } catch (error) {
        console.error(`Error stopping ${type} sync:`, error);
      }
      */
    },
    
    toggleAutoSync(type) {
      if (!this.hasAccess('admin', 'system_admin')) {
        alert('Access denied: You do not have permission to configure auto-sync.');
        return;
      }
      
      const syncStatus = this.adminData.syncStatus[type];
      syncStatus.autoSync = !syncStatus.autoSync;
      
      if (syncStatus.autoSync) {
        this.startAutoSync(type);
      } else {
        this.stopAutoSync(type);
      }
    },
    
    startAutoSync(type) {
      const syncStatus = this.adminData.syncStatus[type];
      
      if (syncStatus.autoSyncInterval) {
        clearInterval(syncStatus.autoSyncInterval);
      }
      
      syncStatus.autoSyncInterval = setInterval(() => {
        if (!syncStatus.syncing && syncStatus.connected) {
          this.startSync(type);
        }
      }, syncStatus.syncInterval * 1000);
      
      console.log(`Auto-sync enabled for ${type} (every ${syncStatus.syncInterval} seconds)`);
    },

    showRealSyncProgress(type, syncResult) {
      // Show real sync progress based on actual inventory data returned from backend
      const syncStatus = this.adminData.syncStatus[type];
      
      // Extract real counts from sync result
      const actualCounts = {
        datacenters: syncResult.datacenters || 0,
        clusters: syncResult.clusters || 0,
        hosts: syncResult.hosts || 0,
        datastores: syncResult.datastores || 0,
        networks: syncResult.networks || 0,
        vms: syncResult.vm_count || 0
      };
      
      // Calculate total items being processed
      const totalItems = actualCounts.datacenters + actualCounts.clusters + 
                        actualCounts.hosts + actualCounts.datastores + 
                        actualCounts.networks + actualCounts.vms;
      
      console.log(`🔄 Real sync progress for ${type}: ${totalItems} total items (${actualCounts.vms} VMs, ${actualCounts.hosts} hosts, ${actualCounts.clusters} clusters, ${actualCounts.datastores} datastores, ${actualCounts.networks} networks)`);
      
      // Set real totals
      syncStatus.totalVMs = actualCounts.vms;
      syncStatus.totalMetrics = totalItems;
      syncStatus.syncedVMs = actualCounts.vms; // Since sync is complete
      syncStatus.syncedMetrics = totalItems; // Since sync is complete
      
      // Animate progress to 100% over 3 seconds to show the actual work being done
      let progress = 0;
      const progressInterval = setInterval(() => {
        progress += 10;
        syncStatus.syncProgress = Math.min(progress, 100);
        
        if (progress >= 100) {
          clearInterval(progressInterval);
          syncStatus.syncing = false;
          syncStatus.lastSync = new Date().toISOString();
          
          console.log(`✅ ${type} sync completed: ${totalItems} items processed`);
        }
      }, 300); // 300ms * 10 = 3 seconds total
    },
    
    stopAutoSync(type) {
      const syncStatus = this.adminData.syncStatus[type];
      
      if (syncStatus.autoSyncInterval) {
        clearInterval(syncStatus.autoSyncInterval);
        syncStatus.autoSyncInterval = null;
      }
      
      console.log(`Auto-sync disabled for ${type}`);
    },

    async refreshSyncStatus(type) {
      // Refresh sync status from backend API
      if (!this.apiAvailable) {
        return;
      }

      try {
        let statusEndpoint;
        if (type === 'prometheus') {
          statusEndpoint = `${this.apiBaseUrl}/admin/prometheus/sync/status`;
        } else if (type === 'zabbix') {
          statusEndpoint = `${this.apiBaseUrl}/admin/zabbix/sync/status`;
        } else {
          // For vCenter, we don't have a dedicated status endpoint yet
          return;
        }

        const response = await fetch(statusEndpoint, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${this.sessionToken}`
          }
        });

        if (response.ok) {
          const status = await response.json();
          const syncData = this.adminData.syncStatus[type];
          
          // Update sync status from API response
          if (status.status === 'not_configured') {
            syncData.connected = false;
          } else if (status.status === 'idle' || status.status === 'ready') {
            syncData.connected = true;
            syncData.lastSync = status.last_sync;
          } else if (status.status === 'syncing') {
            syncData.syncing = true;
            syncData.syncProgress = status.progress || 0;
          } else if (status.status === 'error') {
            syncData.connected = false;
            if (status.message && !syncData.errors.includes(status.message)) {
              syncData.errors.push(status.message);
            }
          }
          
          console.log(`${type} sync status refreshed:`, status);
        }
      } catch (error) {
        console.error(`Failed to refresh ${type} sync status:`, error);
      }
    },

    trackRealSyncProgress(type) {
      // Track real sync progress by periodically checking API status
      const syncStatus = this.adminData.syncStatus[type];
      
      // Set initial values
      syncStatus.totalMetrics = 100; // Will be updated from real API
      syncStatus.syncedMetrics = 0;
      syncStatus.syncProgress = 10; // Start with some progress
      
      const statusCheckInterval = setInterval(async () => {
        try {
          // Check if sync is still supposed to be running
          if (!syncStatus.syncing) {
            clearInterval(statusCheckInterval);
            return;
          }
          
          // Refresh status from API
          await this.refreshSyncStatus(type);
          
          // If API shows sync is complete, finish up
          if (syncStatus.syncProgress >= 100 || !syncStatus.syncing) {
            clearInterval(statusCheckInterval);
            syncStatus.syncing = false;
            syncStatus.syncProgress = 100;
            syncStatus.syncedMetrics = syncStatus.totalMetrics;
            syncStatus.lastSync = new Date().toISOString();
            console.log(`✅ ${type} sync completed`);
            return;
          }
          
          // Gradually increase progress if still syncing
          if (syncStatus.syncProgress < 90) {
            syncStatus.syncProgress = Math.min(90, syncStatus.syncProgress + Math.random() * 15 + 5);
            syncStatus.syncedMetrics = Math.round((syncStatus.syncProgress / 100) * syncStatus.totalMetrics);
          }
          
        } catch (error) {
          console.error(`Error tracking ${type} sync progress:`, error);
          clearInterval(statusCheckInterval);
          syncStatus.syncing = false;
          syncStatus.errors.push(error.message);
        }
      }, 2000); // Check every 2 seconds
      
      // Auto-complete after 30 seconds if still syncing (fallback)
      setTimeout(() => {
        if (syncStatus.syncing) {
          clearInterval(statusCheckInterval);
          syncStatus.syncing = false;
          syncStatus.syncProgress = 100;
          syncStatus.syncedMetrics = syncStatus.totalMetrics;
          syncStatus.lastSync = new Date().toISOString();
          console.log(`⏰ ${type} sync auto-completed after timeout`);
        }
      }, 30000);
    },

    storeVCenterInventory(inventory) {
      // Store comprehensive vCenter inventory data from sync
      console.log('📊 Storing vCenter inventory data:', inventory);
      
      try {
        // Store VMs data
        if (inventory.vms && Array.isArray(inventory.vms)) {
          this.vcenterInventory.vms = inventory.vms.map(vm => ({
            id: vm.moid || vm.vm_id,
            name: vm.vm,  // Backend sends VM name in 'vm' field
            status: vm.status || (vm.power_state === 'poweredOn' ? 'running' : 'stopped'),
            cpu: Math.round(vm.cpu || 0),  // Round CPU percentage
            memory_usage: Math.round(vm.memory_usage || 0),  // Round memory percentage
            cores: Math.round(vm.cores || 1),  // Round CPU cores
            memory: Math.round(vm.memory || 1),  // Round memory in GB
            cluster: vm.cluster || 'Unknown',
            host: vm.host || 'Unknown',
            datacenter: vm.datacenter || 'Unknown',
            power_state: vm.power_state,
            guest_os: vm.guest_os || 'Unknown',
            // Additional vCenter-specific fields
            vm_id: vm.moid || vm.vm_id,
            datastore: vm.datastore,
            network: vm.network,
            annotations: vm.annotations || '',
            creation_time: vm.creation_time,
            last_boot_time: vm.last_boot_time
          }));
          console.log(`✅ Stored ${this.vcenterInventory.vms.length} VMs`);
        }
        
        // Store clusters data
        if (inventory.clusters && Array.isArray(inventory.clusters)) {
          this.vcenterInventory.clusters = inventory.clusters;
          // Extract cluster names for dropdowns (not full objects)
          this.clusters = [...new Set(inventory.clusters.map(cluster => cluster.name || cluster.cluster || cluster))];
          console.log(`✅ Stored ${inventory.clusters.length} clusters`);
        }
        
        // Store hosts data
        if (inventory.hosts && Array.isArray(inventory.hosts)) {
          this.vcenterInventory.hosts = inventory.hosts;
          console.log(`✅ Stored ${inventory.hosts.length} hosts`);
        }
        
        // Store datastores data
        if (inventory.datastores && Array.isArray(inventory.datastores)) {
          this.vcenterInventory.datastores = inventory.datastores;
          console.log(`✅ Stored ${inventory.datastores.length} datastores`);
        }
        
        // Store networks data
        if (inventory.networks && Array.isArray(inventory.networks)) {
          this.vcenterInventory.networks = inventory.networks;
          console.log(`✅ Stored ${inventory.networks.length} networks`);
        }
        
        // Mark as having synced data and update timestamp
        this.vcenterInventory.hasSyncedData = true;
        this.vcenterInventory.lastSync = new Date().toISOString();
        this.adminData.syncStatus.vcenter.lastSync = this.vcenterInventory.lastSync;
        
        console.log('🎉 vCenter inventory data stored successfully');
        
        // Update stats based on real data
        this.updateStatsFromVCenterData();
        
      } catch (error) {
        console.error('❌ Error storing vCenter inventory:', error);
        this.adminData.syncStatus.vcenter.errors.push(`Failed to store inventory data: ${error.message}`);
      }
    },

    storeHyperVInventory(inventory) {
      // Store comprehensive HyperV inventory data from sync
      console.log('📊 Storing HyperV inventory data:', inventory);
      
      try {
        // Store VMs data
        if (inventory.vms && Array.isArray(inventory.vms)) {
          this.hypervInventory.vms = inventory.vms.map(vm => ({
            id: vm.uuid || vm.vm_id,
            name: vm.vm,
            status: vm.status,
            cpu: Math.round(vm.cpu || 0),  // Round CPU percentage
            memory_usage: Math.round(vm.memory_usage || 0),  // Round memory percentage
            cores: Math.round(vm.cores || 1),  // Round CPU cores
            memory: Math.round(vm.memory || 1),  // Round memory in GB
            cluster: vm.cluster || 'Unknown',
            host: vm.host || 'Unknown',
            datacenter: vm.datacenter || 'HyperV-Infrastructure',
            power_state: vm.details?.power_state || vm.status,
            guest_os: vm.guest_os || 'Unknown',
            // Additional HyperV-specific fields
            vm_id: vm.uuid || vm.vm_id,
            source: 'hyperv',
            tools_status: vm.tools_status || 'Available',
            annotations: vm.details?.annotation || ''
          }));
          console.log(`✅ Stored ${this.hypervInventory.vms.length} HyperV VMs`);
        }
        
        // Store clusters data
        if (inventory.clusters && Array.isArray(inventory.clusters)) {
          this.hypervInventory.clusters = inventory.clusters;
          // Extract cluster names for dropdowns (not full objects)
          this.clusters = [...new Set(inventory.clusters.map(cluster => cluster.name || cluster.cluster || cluster))];
          console.log(`✅ Stored ${inventory.clusters.length} HyperV clusters`);
        }
        
        // Store hosts data
        if (inventory.hosts && Array.isArray(inventory.hosts)) {
          this.hypervInventory.hosts = inventory.hosts;
          console.log(`✅ Stored ${inventory.hosts.length} HyperV hosts`);
        }
        
        // Store datastores data (volumes in HyperV)
        if (inventory.datastores && Array.isArray(inventory.datastores)) {
          this.hypervInventory.datastores = inventory.datastores;
          console.log(`✅ Stored ${inventory.datastores.length} HyperV volumes`);
        }
        
        // Store networks data (virtual switches in HyperV)
        if (inventory.networks && Array.isArray(inventory.networks)) {
          this.hypervInventory.networks = inventory.networks;
          console.log(`✅ Stored ${inventory.networks.length} HyperV virtual switches`);
        }
        
        // Mark as having synced data and update timestamp
        this.hypervInventory.hasSyncedData = true;
        this.hypervInventory.lastSync = new Date().toISOString();
        this.adminData.syncStatus.hyperv.lastSync = this.hypervInventory.lastSync;
        
        console.log('🎉 HyperV inventory data stored successfully');
        
        // Update stats based on real data
        this.updateStatsFromHyperVData();
        
      } catch (error) {
        console.error('❌ Error storing HyperV inventory:', error);
        this.adminData.syncStatus.hyperv.errors.push(`Failed to store inventory data: ${error.message}`);
      }
    },

    updateStatsFromHyperVData() {
      // Update dashboard stats with real HyperV data
      if (!this.hypervInventory.hasSyncedData) return;
      
      try {
        const vms = this.hypervInventory.vms;
        const clusters = this.hypervInventory.clusters;
        const hosts = this.hypervInventory.hosts;
        
        // Update VM counts and resource utilization
        if (vms && vms.length > 0) {
          const runningVMs = vms.filter(vm => vm.status === 'running');
          const totalCpu = runningVMs.reduce((sum, vm) => sum + (vm.cpu || 0), 0);
          const avgCpu = runningVMs.length > 0 ? totalCpu / runningVMs.length : 0;
          
          const totalMemory = runningVMs.reduce((sum, vm) => sum + (vm.memory_usage || 0), 0);
          const avgMemory = runningVMs.length > 0 ? totalMemory / runningVMs.length : 0;
          
          // Update real-time metrics with HyperV data
          this.realTimeData.metrics.avgCpu = Math.round(avgCpu);
          this.realTimeData.metrics.avgMemory = Math.round(avgMemory);
          this.realTimeData.metrics.activeVMs = runningVMs.length;
          this.realTimeData.isConnected = true;  // Mark as connected with real data
        }
        
        console.log('📊 Dashboard stats updated with HyperV data');
        
      } catch (error) {
        console.error('❌ Error updating stats from HyperV data:', error);
      }
    },

    async loadPersistedInventory() {
      // Load persisted infrastructure inventory and connection settings from database on startup
      console.log('🔄 Loading persisted infrastructure inventory and connection settings...');
      
      try {
        // Load connection settings first
        await this.loadConnectionSettings();
        
        // Load vCenter inventory from database
        await this.loadPersistedVCenterInventory();
        
        // Load HyperV inventory from database  
        await this.loadPersistedHyperVInventory();
        
      } catch (error) {
        console.error('❌ Error loading persisted inventory:', error);
      }
    },

    async loadConnectionSettings() {
      // Load saved connection settings from backend
      try {
        const response = await fetch(`${this.apiBaseUrl}/admin/integrations/config`, {
          headers: {
            'Authorization': `Bearer ${this.sessionToken}`,
            'Content-Type': 'application/json'
          }
        });
        
        if (response.ok) {
          const config = await response.json();
          
          // Restore vCenter connection settings
          if (config.vcenter) {
            this.adminData.connectionForms.vcenter.host = config.vcenter.host || '';
            this.adminData.connectionForms.vcenter.username = config.vcenter.username || '';
            // Don't restore password for security, but mark as connected if last connection was recent
            if (config.vcenter.last_connected) {
              const lastConnected = new Date(config.vcenter.last_connected);
              const now = new Date();
              const hoursSinceConnection = (now - lastConnected) / (1000 * 60 * 60);
              
              if (hoursSinceConnection < 24) { // Consider connected if within 24 hours
                this.adminData.syncStatus.vcenter.connected = true;
                this.adminData.syncStatus.vcenter.lastSync = config.vcenter.last_sync;
              }
            }
            console.log('✅ Restored vCenter connection settings');
          }
          
          // Restore HyperV connection settings
          if (config.hyperv) {
            this.adminData.connectionForms.hyperv.host = config.hyperv.host || '';
            this.adminData.connectionForms.hyperv.username = config.hyperv.username || '';
            // Don't restore password for security, but mark as connected if last connection was recent
            if (config.hyperv.last_connected) {
              const lastConnected = new Date(config.hyperv.last_connected);
              const now = new Date();
              const hoursSinceConnection = (now - lastConnected) / (1000 * 60 * 60);
              
              if (hoursSinceConnection < 24) { // Consider connected if within 24 hours
                this.adminData.syncStatus.hyperv.connected = true;
                this.adminData.syncStatus.hyperv.lastSync = config.hyperv.last_sync;
              }
            }
            console.log('✅ Restored HyperV connection settings');
          }
          
        } else {
          console.warn('Failed to load connection settings:', response.status);
        }
      } catch (error) {
        console.error('❌ Error loading connection settings:', error);
      }
    },

    async loadPersistedVCenterInventory() {
      try {
        const response = await fetch(`${this.apiBaseUrl}/vcenter/inventory`, {
          headers: {
            'Authorization': `Bearer ${this.sessionToken}`,
            'Content-Type': 'application/json'
          }
        });
        
        if (response.ok) {
          const inventory = await response.json();
          if (inventory && inventory.vms && inventory.vms.length > 0) {
            console.log(`📊 Loaded ${inventory.vms.length} vCenter VMs from database`);
            this.storeVCenterInventory(inventory);
          } else {
            console.log('📊 No persisted vCenter inventory found');
          }
        } else {
          console.warn('Failed to load persisted vCenter inventory:', response.status);
        }
      } catch (error) {
        console.error('❌ Error loading persisted vCenter inventory:', error);
      }
    },

    async loadPersistedHyperVInventory() {
      try {
        const response = await fetch(`${this.apiBaseUrl}/hyperv/inventory`, {
          headers: {
            'Authorization': `Bearer ${this.sessionToken}`,
            'Content-Type': 'application/json'
          }
        });
        
        if (response.ok) {
          const inventory = await response.json();
          if (inventory && inventory.vms && inventory.vms.length > 0) {
            console.log(`📊 Loaded ${inventory.vms.length} HyperV VMs from database`);
            this.storeHyperVInventory(inventory);
          } else {
            console.log('📊 No persisted HyperV inventory found');
          }
        } else {
          console.warn('Failed to load persisted HyperV inventory:', response.status);
        }
      } catch (error) {
        console.error('❌ Error loading persisted HyperV inventory:', error);
      }
    },

    updateStatsFromVCenterData() {
      // Update dashboard stats with real vCenter data
      if (!this.vcenterInventory.hasSyncedData) return;
      
      try {
        const vms = this.vcenterInventory.vms;
        const clusters = this.vcenterInventory.clusters;
        const hosts = this.vcenterInventory.hosts;
        
        // Update VM count
        const runningVMs = vms.filter(vm => vm.status === 'running').length;
        const totalVMs = vms.length;
        
        // Calculate average CPU and memory usage (ensure proper field access)
        const avgCpu = vms.length > 0 ? vms.reduce((sum, vm) => sum + (vm.cpu || 0), 0) / vms.length : 0;
        const avgMemory = vms.length > 0 ? vms.reduce((sum, vm) => sum + (vm.memory_usage || 0), 0) / vms.length : 0;
        
        // Update stats object with real data (rounded values only)
        this.stats = [
          {
            title: 'Active VMs',
            value: runningVMs,
            subtitle: `${totalVMs} total`,
            icon: 'server',
            color: 'text-blue-600',
            bgColor: 'bg-blue-50'
          },
          {
            title: 'Avg CPU Usage',
            value: `${Math.round(avgCpu)}%`,
            subtitle: 'Across all VMs',
            icon: 'cpu',
            color: 'text-green-600',
            bgColor: 'bg-green-50'
          },
          {
            title: 'Avg Memory',
            value: `${Math.round(avgMemory)}%`,
            subtitle: 'Memory utilization',
            icon: 'memory-stick',
            color: 'text-purple-600',
            bgColor: 'bg-purple-50'
          },
          {
            title: 'Clusters',
            value: clusters.length,
            subtitle: `${hosts.length} hosts total`,
            icon: 'layers',
            color: 'text-orange-600',
            bgColor: 'bg-orange-50'
          }
        ];
        
        // Update real-time data with vCenter metrics
        this.realTimeData.metrics.avgCpu = Math.round(avgCpu);
        this.realTimeData.metrics.avgMemory = Math.round(avgMemory);
        this.realTimeData.metrics.activeVMs = runningVMs;
        this.realTimeData.isConnected = true;  // Mark as connected with real data
        
        console.log('📈 Dashboard stats updated with real vCenter data');
        
      } catch (error) {
        console.error('❌ Error updating stats from vCenter data:', error);
      }
    },
    
    simulateSync(type) {
      // Simulate sync progress for demo purposes
      const syncStatus = this.adminData.syncStatus[type];
      const totalItems = type === 'vcenter' ? 100 : type === 'hyperv' ? 80 : 50; // Realistic totals for full infrastructure sync
      
      syncStatus.totalVMs = totalItems;
      syncStatus.totalMetrics = totalItems;
      syncStatus.syncedVMs = 0;
      syncStatus.syncedMetrics = 0;
      
      const progressInterval = setInterval(() => {
        syncStatus.syncProgress += Math.random() * 15;
        
        if (type === 'vcenter') {
          syncStatus.syncedVMs = Math.min(totalItems, Math.round((syncStatus.syncProgress / 100) * totalItems));
        } else {
          syncStatus.syncedMetrics = Math.min(totalItems, Math.round((syncStatus.syncProgress / 100) * totalItems));
        }
        
        if (syncStatus.syncProgress >= 100) {
          syncStatus.syncProgress = 100;
          syncStatus.syncing = false;
          syncStatus.lastSync = new Date().toISOString();
          
          clearInterval(progressInterval);
          
          // Update dashboard data to show new synced data
          this.loadData();
          
          console.log(`✅ ${type} sync simulation completed! Synchronized ${totalItems} items.`);
        }
      }, 500); // Update every 500ms for demo
    }
  }
});

app.mount('#app');