<script>
  import { Doughnut } from 'svelte-chartjs'

  import {
    AREA_BORDER,
    TASK_ACTION_VALUES,
    TASK_ACTION_TEXT,
    TASK_COLORS,
    TASK_STATUS_VALUES,
  } from '$lib/config.js'

  export let stats
  console.info(stats)

  const options = {
    backgroundColor: [
      TASK_COLORS['READY'].substring(0, 7),
      TASK_COLORS['MAPPED'],
      TASK_COLORS['VALIDATED'],
      TASK_COLORS['INVALIDATED'],
      TASK_COLORS['NEED_UPDATE'],
      '#ff69b499',
      '#ff00ff99',
    ],
    hoverBackgroundColor: [
      '#dddddd',
      TASK_COLORS['MAPPED'].substring(0, 7),
      TASK_COLORS['VALIDATED'].substring(0, 7),
      TASK_COLORS['INVALIDATED'].substring(0, 7),
      TASK_COLORS['NEED_UPDATE'].substring(0, 7),
      '#ff69b4',
      '#ff00ff',
    ],
    borderColor: AREA_BORDER,
    borderWidth: 1,
  }

  const data = {
    labels: stats.labels,
    datasets: [
      {
        label: 'Edificios',
        data: stats.buildings,
        ...options,
      },
      {
        label: 'Direcciones',
        data: stats.addresses,
        ...options,
      },
    ],
  }

  import {
    Chart as ChartJS,
    Title,
    Tooltip,
    Legend,
    ArcElement,
    CategoryScale,
  } from 'chart.js'
  
  ChartJS.register(Title, Tooltip, Legend, ArcElement, CategoryScale)
</script>
  
<Doughnut
  {data}
  options={{
    responsive: true,
    plugins: {
      legend: {
        position: 'right',
      },
    },
  }}
/>
