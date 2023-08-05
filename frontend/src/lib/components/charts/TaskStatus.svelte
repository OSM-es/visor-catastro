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

  import {
    AREA_BORDER,
    TASK_COLORS,
  } from '$lib/config.js'
  import { t } from '$lib/translations'

  export let stats

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
    labels: getLabels(stats.labels),
    datasets: [
      {
        label: $t('explore.Buildings'),
        data: stats.buildings,
        ...options,
      },
      {
        label: $t('explore.Addresses'),
        data: stats.addresses,
        ...options,
      },
    ],
  }

  function getLabels(labels) {
    return labels.map((label) => $t('explore.' + label))
  }
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
