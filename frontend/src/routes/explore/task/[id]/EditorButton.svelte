<script>
  import { goto } from '$app/navigation'

  import { Button } from 'flowbite-svelte'

  export let action
  export let user
  export let task

  function doTutorial() {
    goto('/learn/' + (user?.tutorial ? user.tutorial.next : 'login'))
  }

  function gotoCurrentTask() {
    window.location = `/explore/task/${task.currentLock}`
  }
</script>

{#if task.currentLock}
  <p>
    Tienes otra tarea bloqueada
    <Button on:click={gotoCurrentTask}>Complétala</Button>
  </p>
{:else if user?.role == 'READ_ONLY'}
  <p>Usuario sin permiso de edición</p>
{:else if user?.role}
  <slot/>
{:else}
  <Button on:click={doTutorial}>Completa el tutorial para {action}</Button>
{/if}
