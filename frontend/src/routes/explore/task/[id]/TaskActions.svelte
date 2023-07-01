<script>
  import { Button } from 'flowbite-svelte'

  import { TASK_STATUS_VALUES } from '$lib/config'
  import EditorButton from './EditorButton.svelte'

  export let status
  export let user
  export let mapper
  export let validator
  export let task
</script>

{#if status.includes('LOCKED')}
  {#if task.owner.id !== user.id}
    <p>
      Tarea
      <span class="font-bold text-danger-500">bloqueada</span>, otro usuario la está
      <span class="lowercase">{TASK_STATUS_VALUES[status]}</span>.
    </p>
  {:else}
    <p>Diálogo para mapear.</p>
  {/if}
{:else if status === 'MAPPED'}
  <p>
    Tarea
    <span class="text-success-500 font-bold">mapeada</span>{#if user.id === mapper.id},
      otro usuario debe validarla.
    {:else}
      {' '}por {mapper.display_name}
      <EditorButton {user} action={'validar'}>
        <Button>Valídala</Button>
      </EditorButton>
    {/if}
  </p>
{:else if status === 'VALIDATED'}
  <p>
    Tarea <span class="text-success-500 font-bold">validada</span>
    {#if user.id !== validator.id}
      por <span class="font-semibold">{validator.display_name}</span>
    {/if}
  </p>
{/if}
