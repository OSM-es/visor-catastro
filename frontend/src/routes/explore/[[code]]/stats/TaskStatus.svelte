<script>
  import { Card, CardPlaceholder } from 'flowbite-svelte'
  import Doughnut from '$lib/components/charts/Doughnut.svelte'
  import StatsSection from '$lib/components/StatsSection.svelte'
  import { AREA_BORDER, TASK_COLORS } from '$lib/config.js'
  import { t } from '$lib/translations'

  export let fetchData

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

  function getLabels(stats) {
    return Object.keys(stats).map((label) => $t('explore.' + label))
  }

  function getData(stats) {
    return {
      labels: getLabels(stats.buildings),
      datasets: [
        {
          label: $t('explore.Buildings'),
          data: Object.values(stats.buildings),
          ...options,
        },
        {
          label: $t('explore.Addresses'),
          data: Object.values(stats.addresses),
          ...options,
        },
      ],
    }
  }
</script>

<div>
  <h2 class="text-2xl font-bold mb-4">{$t('stats.taskstatus')}</h2>
  <div class="flex flex-col md:flex-row gap-x-8 gap-y-4">
    {#await fetchData}
      <CardPlaceholder class="w-full md:w-1/3 h-96" size="xl"/>
      <CardPlaceholder class="w-full md:w-2/3 h-96" size="2xl"/>
    {:then stats}
      <Card class="w-full md:w-1/3 h-96" size="xl">
        <Doughnut data={getData(stats)}/>
      </Card>
      <Card class="w-full md:w-2/3 min-h-96" size="xl">
        {#if stats.splitted}
          <h3 class="text-xl font-bold mb-4">{$t('explore.Buildings')} / {$t('explore.addresses')}</h3>
          <StatsSection stats={stats.buildings} stats2={stats.addresses} ns={'explore'} gap={'gap-x-24'}/>
          {:else}
          <StatsSection stats={stats.buildings} ns={'explore'} gap={'gap-x-24'}/>
        {/if}
      </Card>
    {/await}
  </div>
</div>