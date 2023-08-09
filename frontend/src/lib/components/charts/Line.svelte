<script>
  import { Line } from 'svelte-chartjs'
  import {
    Chart as ChartJS,
    Colors,
    LineController,
    ScatterController,
    PointElement,
    Legend,
    LineElement,
    Tooltip,
    LinearScale,
    TimeScale,
  } from 'chart.js'
  import 'chartjs-adapter-date-fns'
  import { locale } from '$lib/translations'

  $: format = $locale === 'en' ? 'Y-M-d' : 'd/M/Y'
  
  ChartJS.register(
    Colors,
    LineController,
    Tooltip,
    ScatterController,
    PointElement,
    Legend,
    LineElement,
    LinearScale,
    TimeScale,
  )

  export let data
</script>
  
<Line
  {data}
  options={{
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { display: true } },
    scales: { 
      x: { 
        type: 'time',
        time: {
          unit: 'day',
          displayFormats: { day: format },
          tooltipFormat: format,
        }
      }
    },
  }}
/>
