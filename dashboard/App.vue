
<template>
  <div class="p-4 font-sans">
    <h1 class="text-2xl font-bold mb-4">IROA Dashboard</h1>
    <div v-if="recommendations.length">
      <h2 class="text-xl mb-2">Recommendations</h2>
      <ul>
        <li v-for="rec in recommendations" :key="rec.vm" class="border p-2 mb-2 rounded">
          <strong>{{ rec.vm }}</strong>: {{ rec.suggestion }}
        </li>
      </ul>
    </div>
    <div v-else>Loading recommendations...</div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      recommendations: []
    }
  },
  async mounted() {
    const res = await fetch("http://localhost:8001/recommendations")
    this.recommendations = await res.json()
  }
}
</script>
