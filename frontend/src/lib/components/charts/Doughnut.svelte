<script>
  import { Doughnut } from 'svelte-chartjs'

  import {
    Chart as ChartJS,
    Title,
    Tooltip,
    Legend,
    ArcElement,
    CategoryScale,
  } from 'chart.js'
  
  ChartJS.register(Title, Tooltip, Legend, ArcElement, CategoryScale)

  export let data

  function setPercents(data) {
    data.datasets.forEach((dataset, i) => {
      const total = dataset.data.reduce((a, b) => a + b, 0)
      dataset.data = dataset.data.map((v) => Math.round((v / total) * 100));
    })
    return data
  }

  function formatTooltip(context) {
    let label = context.label
    if (label) label += ': '
    label += context.dataset.data[context.dataIndex]
    return label + '%'
  }
</script>
  
<Doughnut
  data={setPercents(data)}
  options={{
    responsive: true,
    plugins: {
      legend: { position: 'right', labels: { boxWidth: 24 } },
      tooltip: { callbacks: { label: (context) => formatTooltip(context) } },
    },
  }}
/>
