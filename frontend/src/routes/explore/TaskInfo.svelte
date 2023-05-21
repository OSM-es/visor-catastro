<script>
	import { createEventDispatcher } from 'svelte'
  import { Button, Input } from 'flowbite-svelte'
  
  export let task
  export let edit = false
  
  let value = task.properties.status

  const dispatch = createEventDispatcher()

  function handleSave() {
    task.properties.status = value
    dispatch('update')
  }
</script>

<div class="prose lg:prose-xl dark:prose-invert">
  <ul>
    <li>Código de municipio: {task.properties.muncode}</li>
    <li>Referencia: {task.properties.localid}</li>
    <li>Tipo: {task.properties.type}</li>
    <li>Partes de edificio: {task.properties.parts}</li>
    {#if edit}
      <li>
        Estado:
        <Input type=number bind:value min=0 max=9 />
      </li>
      <Button on:click={() => dispatch('update')} color="alternative">Cancelar</Button>
      <Button on:click={handleSave}>Guardar</Button>
    {:else}
      <li>Estado: {task.properties.status}</li>
    {/if}
  </ul>
</div>
