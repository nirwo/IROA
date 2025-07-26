<template>
  <div class="bg-white rounded-xl shadow-sm p-6 card-hover border border-gray-200">
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
      <div class="flex items-center space-x-2">
        <span :class="[
          'inline-flex px-2 py-1 text-xs font-semibold rounded-full',
          vm.status === 'running' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
        ]">
          {{ vm.status }}
        </span>
      </div>
    </div>
    
    <!-- Resource Usage -->
    <div class="space-y-3">
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
    <div class="mt-4 pt-4 border-t border-gray-100">
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
    <div class="mt-4 flex space-x-2">
      <button 
        @click="$emit('view-details', vm)"
        class="flex-1 bg-indigo-600 text-white px-3 py-2 rounded-lg text-sm font-medium hover:bg-indigo-700 transition-colors"
      >
        View Details
      </button>
      <button 
        @click="$emit('get-forecast', vm.id)"
        class="flex-1 bg-gray-100 text-gray-700 px-3 py-2 rounded-lg text-sm font-medium hover:bg-gray-200 transition-colors"
      >
        Forecast
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'VMCard',
  props: {
    vm: {
      type: Object,
      required: true
    }
  },
  emits: ['view-details', 'get-forecast']
}
</script>
