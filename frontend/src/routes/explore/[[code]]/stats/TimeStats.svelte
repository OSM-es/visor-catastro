<script>
  import humanizeDuration from 'humanize-duration'
  import Line from '$lib/components/charts/Line.svelte'
  import { Card, CardPlaceholder } from 'flowbite-svelte'

  import { locale, t } from '$lib/translations'
  import StatsSection from '$lib/components/StatsSection.svelte'

  export let fetchData

  function getChartData(stats) {
    return {
      datasets: [
        { label: $t('stats.mappedtasks'), data: stats.mapped_tasks_per_day },
        { label: $t('stats.validatedtasks'), data: stats.validated_tasks_per_day },
      ],
    }
  }

  function getSectionData(stats) {
    const options = { language: $locale, largest: 1, round: true }
    stats.average_mapping_time = humanizeDuration(stats.average_mapping_time * 1000, options)
    stats.average_validation_time = (
      stats.average_validation_time
      ? humanizeDuration(stats.average_validation_time * 1000, options)
      : '-'
    )
    stats.time_to_finish_mapping = humanizeDuration(stats.time_to_finish_mapping * 1000, options)
    stats.time_to_finish_validation = (
      stats.time_to_finish_validation
      ? humanizeDuration(stats.time_to_finish_validation * 1000, options)
      : '-'
    )
    return stats
  }
</script>

<div>
  <h2 class="text-2xl font-bold mb-4">{$t('stats.timestats')}</h2>
  <div class="flex flex-col md:flex-row gap-x-8 gap-y-4">
    {#await fetchData}
      <CardPlaceholder class="w-full md:w-2/3 h-96" size="2xl"/>
    {:then stats}
      <Card class="w-full" size="2xl">
        <div class="flex flex-col md:flex-row gap-x-20 gap-y-8">
          <div class="w-full md:w-1/2 h-96">
            <Line data={getChartData(stats)}/>
          </div>
          <div class="w-full md:w-1/2">
            <StatsSection
              stats={getSectionData(stats)}
              ns={'stats'}
              gap={'gap-x-20'}
              omit={['mapped_tasks_per_day', 'validated_tasks_per_day']}
            />
          </div>
        </div>
      </Card>
    {/await}
  </div>
</div>