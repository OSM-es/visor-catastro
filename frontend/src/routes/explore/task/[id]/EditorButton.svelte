<script>  
  import { Button } from 'flowbite-svelte'
  
  import { goto } from '$app/navigation'
  import { login } from '$lib/user'
  import { t } from '$lib/translations'

  export let action
  export let user
  export let task

  function doTutorial() {
    goto('/learn/' + (user?.tutorial ? user.tutorial.next : 'login'))
  }

  function gotoCurrentTask() {
    goto(`/explore/task/${task.currentLock}`)
  }
</script>

{#if task.currentLock && task.currentLock !== task.id}
  <p>
    {$t('task.userlockanothertask')}
    <Button on:click={gotoCurrentTask}>{$t('task.completeit')}</Button>
  </p>
{:else if user?.role == 'READ_ONLY'}
  <p>{$t('task.readonly')}</p>
{:else if user?.role}
  <slot/>
{:else if !user}
  <Button on:click={login}>{$t('task.signin', { action })}</Button>
{:else}
  <Button on:click={doTutorial}>{$t('task.dotutorial', { action })}</Button>
{/if}
