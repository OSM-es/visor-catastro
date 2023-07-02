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

<input name="addresses" value={status === task.ad_status} hidden/>
<input name="buildings" value={status === task.bu_status} hidden/>
{#if task.is_locked}
  {#if task.owner.id !== user.id}
    <p>
      Tarea
      <span class="font-bold text-danger-500">bloqueada</span>, otro usuario la está
      <span class="lowercase">{TASK_STATUS_VALUES[task.is_locked]}</span>.
    </p>
  {:else if status === 'LOCKED_FOR_MAPPING'}
    <p>Diálogo para mapear.</p>
  {:else if status === 'LOCKED_FOR_VALIDATION'}
    <p>¿Esta tarea está bien mapeada? Si/No. Enviar tarea Detener validación</p>
  {/if}
{:else if status === 'MAPPED'}
  <p>
    Tarea
    <span class="text-success-500 font-bold">mapeada</span>{#if user.id === mapper?.id},
      otro usuario debe validarla.
    {:else}
      {' '}por {mapper?.display_name}
      <EditorButton {user} action={'validar'}>
        <Button type="submit" name="status" value="LOCKED_FOR_VALIDATION">
          Valídala
        </Button>
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
