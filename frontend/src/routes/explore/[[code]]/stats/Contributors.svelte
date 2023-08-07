<script>
  import { t } from '$lib/translations'
  import { Avatar, Card, CardPlaceholder, Tooltip } from 'flowbite-svelte'
  import Bar from '$lib/components/charts/Bar.svelte'
  import Doughnut from '$lib/components/charts/Doughnut.svelte'
  import StatsSection from '$lib/components/StatsSection.svelte'

  export let fetchData

  function getPastMonths(months) {
    let today = new Date()
    return today.setMonth(today.getMonth() - months)
  }

  function getExperience(date) {
    const months = [[0, 1], [1, 3], [3, 6], [6, 12]]
    return months.findIndex((m) => {
      return new Date(date) > getPastMonths(m[1]) && new Date(date) <= getPastMonths(m[0])
    })
  }

  function getUsersByExperience(contributors) {
    const labels = [1, 2, 3, 4, 5].map(k => $t('stats.experience' + k))
    const data = [0, 0, 0, 0, 0]
    contributors.reduce((data, user) => {
      data[getExperience(user.user.date_registered)] += 1
      return data
    }, data)
    return {  labels, datasets: [{ data }] }
  }

  function getUsersByLevel(contributors) {
    const stats = { BEGINNER: 0, INTERMEDIATE: 0, ADVANCED: 0}
    contributors.reduce((stats, user) => {
      stats[user.user.mapping_level] += 1
      return stats
    }, stats)
    return {
      labels: Object.keys(stats).map(k => $t('common.' + k)),
      datasets: [{ data: Object.values(stats) }],
    }
  }
</script>

<div>
  <h2 class="text-2xl font-bold mb-4">{$t('stats.contributors')}</h2>
  <div class="flex flex-col md:flex-row gap-x-8 gap-y-4">
    {#await fetchData}
      <CardPlaceholder class="w-full md:w-1/3" size="xl"/>
      <CardPlaceholder class="w-full md:w-1/3" size="xl"/>
      <CardPlaceholder class="w-full md:w-1/3" size="xl"/>
    {:then data}
      <Card class="w-full md:w-1/3" size="xl">
        <div class="flex px-4 mb-4">
          {#each data.contributors as user}
            <Avatar data-name={user.display_name} src={user?.img} stacked/>
          {/each}
          <Tooltip triggeredBy="[data-name]" on:show={e => name = e.target.dataset.name}>{name}</Tooltip>
        </div>
        <StatsSection
          stats={{ contribtotal: data.contributors.length, ...data }}
          omit={'contributors'}
          gap={'gap-x-12'}
        />
      </Card>
      <Card class="w-full md:w-1/3 h-96" size="xl">
        <h3 class="text-xl font-bold mb-4">{$t('stats.usersbyexperience')}</h3>
        <div class="h-full">
          <Bar data={getUsersByExperience(data.contributors)}/>
        </div>
      </Card>
      <Card class="w-full md:w-1/3 h-96" size="xl">
        <h3 class="text-xl font-bold mb-4">{$t('stats.usersbylevel')}</h3>
        <div class="h-full">
          <Doughnut data={getUsersByLevel(data.contributors)}/>
        </div>
      </Card>
    {/await}
  </div>
</div>
