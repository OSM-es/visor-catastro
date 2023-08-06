<script>
  import { t } from '$lib/translations'
  import { Spinner } from 'flowbite-svelte'

  import TaskStatus from './TaskStatus.svelte';

  export let data
</script>

<div class="m-8">
  <!--h1>{$t('explore.cadastreof')} {data.task.municipality.name} ({data.code})</h1-->
  {#await data.streamed.taskStatus}
    <p class="mt-4">{$t('common.loading')} <Spinner size={4}/></p>
  {:then stats}
    <TaskStatus {stats}/>
  {/await}
</div>