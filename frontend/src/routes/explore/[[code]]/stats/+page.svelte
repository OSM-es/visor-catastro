<script>
  import { t } from '$lib/translations'

  import TaskStatus from './TaskStatus.svelte';
  import Contributors from './Contributors.svelte';

  export let data
</script>

<div class="m-8 space-y-8 pb-8">
  <h1 class="text-3xl font-bold">
    {$t('explore.cadastreof')} {data.municipality.name} ({data.municipality.muncode})
  </h1>
  <TaskStatus fetchData={data.streamed.taskStatus}/>
  <Contributors fetchData={data.streamed.contributors}/>
</div>