
import { defineComponent, onMounted, ref } from 'vue'
import Chart from 'chart.js/auto'

export default defineComponent({
  name: 'TrendChart',
  props: ['label', 'data'],
  setup(props) {
    const canvasRef = ref(null)

    onMounted(() => {
      new Chart(canvasRef.value, {
        type: 'line',
        data: {
          labels: props.data.map((_, i) => i),
          datasets: [{
            label: props.label,
            data: props.data,
            borderColor: 'rgba(75, 192, 192, 1)',
            tension: 0.1,
            fill: false
          }]
        },
        options: {
          responsive: true,
          plugins: { legend: { display: true } },
          scales: { y: { beginAtZero: true } }
        }
      })
    })

    return { canvasRef }
  },
  template: `<canvas ref="canvasRef" width="400" height="200"></canvas>`
})
