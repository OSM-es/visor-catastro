<script>
  import { Doughnut } from 'svelte-chartjs'

  import {
    Chart as ChartJS,
    Colors,
    Tooltip,
    Legend,
    ArcElement,
    CategoryScale,
  } from 'chart.js'
  
  ChartJS.register(Colors, Tooltip, Legend, ArcElement, CategoryScale)

  export let data

  function formatTooltip(context) {
    const total = context.dataset.data.reduce((a, b) => a + b, 0)
    let label = context.dataset.label || ''
    if (label) label += ': '
    label += `${context.raw} (${Math.round((context.raw / total) * 100)}%)`
    return label
  }
</script>
  
<Doughnut
  {data}
  options={{
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { position: 'right', labels: { boxWidth: 24 } },
      tooltip: { callbacks: { label: (context) => formatTooltip(context) } },
    },
  }}
/>
