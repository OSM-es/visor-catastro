<script>
  import { Spinner } from 'flowbite-svelte'

  import TaskStatus from '$lib/components/charts/TaskStatus.svelte'
  import { t } from '$lib/translations'

  export let data
</script>

<div class="flex">
  <div class="w-1/3">
    {#await data.streamed.taskStatus}
      <p class="mt-4">{$t('common.loading')} <Spinner size={4}/></p>
    {:then stats}
      <TaskStatus stats={stats}/>
    {/await}
  </div>
</div>