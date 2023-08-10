<script>
  import { t } from '$lib/translations'
  import { ArrowUturnLeft } from 'svelte-heros-v2'

  import TaskStatus from './TaskStatus.svelte'
  import Contributors from './Contributors.svelte'
  import TimeStats from './TimeStats.svelte'

  export let data
</script>

<div class="m-8 space-y-8 pb-8">
  <h1 class="text-3xl font-bold">
    <a href={`/explore/${data.municipality.muncode}`} class="flex items-center justify-between">
      {$t('explore.cadastreof')} {data.municipality.name} ({data.municipality.muncode})
      <ArrowUturnLeft/>
    </a>
  </h1>
  <TaskStatus fetchData={data.streamed.taskStatus}/>
  <Contributors fetchData={data.streamed.contributors}/>
  <TimeStats fetchData={data.streamed.timeStats}/>
</div>