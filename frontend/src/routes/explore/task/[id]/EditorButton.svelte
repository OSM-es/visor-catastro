<script>
  import { goto } from '$app/navigation'

  import { Button } from 'flowbite-svelte'

  export let user
  export let action

  function doTutorial() {
    goto('/learn/' + (user?.tutorial ? user.tutorial.next : 'login'))
  }
</script>

{#if user?.role && user.role != 'READ_ONLY'}
  <slot/>
{:else}
  <Button on:click={doTutorial}>Completa el tutorial para {action}</Button>
{/if}
