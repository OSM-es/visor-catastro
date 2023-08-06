<script>
  import { Spinner } from 'flowbite-svelte'

  import Doughnut from '$lib/components/charts/Doughnut.svelte'
  import { AREA_BORDER, TASK_COLORS } from '$lib/config.js'
  import { t } from '$lib/translations'

  export let data

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

  function getLabels(labels) {
    return labels.map((label) => $t('explore.' + label))
  }

  function getData(stats) {
    return {
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
  }
</script>

<div class="flex">
  <div class="w-1/3">
    {#await data.streamed.taskStatus}
      <p class="mt-4">{$t('common.loading')} <Spinner size={4}/></p>
    {:then stats}
      <Doughnut data={getData(stats)}/>
    {/await}
  </div>
</div>