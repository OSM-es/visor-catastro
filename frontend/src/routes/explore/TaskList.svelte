<script>
	import { createEventDispatcher } from 'svelte'
  import { goto } from '$app/navigation'

  export let tasks

  const dispatch = createEventDispatcher()
</script>

<div class="prose dark:prose-invert">
{#if !tasks || tasks.length === 0}
  <div>No hay tareas aquí.</div>
{:else}
  <p>Selecciona una tarea.</p>
  <div>
    {#each tasks as task (task.id)}
      <!-- svelte-ignore a11y-click-events-have-key-events -->
      <!-- svelte-ignore a11y-mouse-events-have-key-events -->
      <div
        on:click={() => goto('/explore/task/' + task.properties.id)}
        on:mouseover={() => dispatch('mouseover', { feature: task })}
        on:mouseout={() => dispatch('mouseout')}
        class="hover:bg-amber-400 cursor-pointer"
      >
        {task.properties.muncode}
        {task.properties.localid}
        {task.properties.type}
        {task.properties.parts}
        {task.properties.status}
      </div>
    {/each}
  </div>
{/if}
</div>