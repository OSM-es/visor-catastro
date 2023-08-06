<script>
  import { t } from '$lib/translations'
  import { Spinner } from 'flowbite-svelte'

  import TaskStatus from './TaskStatus.svelte';

  export let data
</script>

<div class="m-8">
  <h1 class="text-3xl font-bold mb-12">
    {$t('explore.cadastreof')} {data.municipality.name} ({data.municipality.muncode})
  </h1>
  {#await data.streamed.taskStatus}
    <p class="mt-4">{$t('common.loading')} <Spinner size={4}/></p>
  {:then stats}
    <TaskStatus {stats}/>
  {/await}
</div>