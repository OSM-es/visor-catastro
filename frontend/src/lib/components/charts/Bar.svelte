<script>
  import { Bar } from 'svelte-chartjs'

  import {
    Chart as ChartJS,
    Colors,
    BarController,
    BarElement,
    Tooltip,
    CategoryScale,
    LinearScale
  } from 'chart.js'
  
  ChartJS.register(Colors, Tooltip, BarController, BarElement, CategoryScale, LinearScale)

  export let data
</script>
  
<Bar
  {data}
  options={{
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { display: false } },
  }}
/>
