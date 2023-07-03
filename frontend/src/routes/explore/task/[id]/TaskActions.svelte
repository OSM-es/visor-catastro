<script>
  import { Button, Checkbox, Radio } from 'flowbite-svelte'

  import { TASK_STATUS_VALUES } from '$lib/config'
  import EditorButton from './EditorButton.svelte'

  export let status
  export let user
  export let mapper
  export let task

  let streetsToValidate = task.streets?.filter(s => !s.validated) || []
  let newStatus
  $: {
    if (status === 'LOCKED_FOR_VALIDATION') {
      newStatus = 'VALIDATED'
    }
  }
</script>

<input name="addresses" value={status === task.ad_status} hidden/>
<input name="buildings" value={status === task.bu_status} hidden/>
{#if status.startsWith('LOCKED_')}
  {task.owner?.id}
  {user?.id}
  {#if task.owner?.id !== user?.id}
    <p>
      Tarea
      <span class="font-bold text-danger-500">bloqueada</span>, otro usuario la está
      <span class="lowercase">{TASK_STATUS_VALUES[task.is_locked]}</span>.
    </p>
  {:else if status === 'LOCKED_FOR_MAPPING'}
    <p>TODO: Aquí faltan enlaces para descargar el archivo de la tarea</p>
    <p>¿Esta tarea está completamente mapeada?</p>
    <Button type="submit" name="status" value="MAPPED" class="mr-4">
      Si, guardar
    </Button>
  {:else if status === 'LOCKED_FOR_VALIDATION'}
    <p>TODO: Aquí faltan enlaces para descargar el archivo de la tarea,
      y el área.
    </p>
    <p>¿Esta tarea está bien mapeada?</p>
    <div class="flex space-x-8 mb-8">
      <Radio
        type="radio"
        name="status"
        value="VALIDATED"
        bind:group={newStatus}
      >
        Si
      </Radio>
      <Radio
        type="radio"
        name="status"
        value="INVALIDATED"
        bind:group={newStatus}
      >
        No
    </Radio>
    </div>
    <Button type="submit" class="mr-4">
      {newStatus === 'VALIDATED' ? 'Validar' : 'Invalidar' }
    </Button>
  {/if}
{:else if status === 'READY'}
  <p>ready</p>
  {#if task.streets?.length}
    <h5>Nombres de calle:</h5>
    <ul class="mt-0">
      {#each task.streets as street}
        <li class="my-0">
            <a href="/explore/{task.muncode}/street/{street.cat_name}">
              {street.cat_name}
            </a>
          {street.validated ? 'Confirmado' : 'Pendiente'}
          </li>
      {/each}
    </ul>
    {#if streetsToValidate}
      <p>
        Falta revisar {streetsToValidate.length}
        {streetsToValidate.length > 1 ? 'nombres' : 'nombre'}
        para poder importar direcciones.
      </p>
    {/if}
  {/if}
  <p>Voy a importar
    <Checkbox name="buildings" checked>Edificios</Checkbox>
    <Checkbox
      name="addresses"
      checked={streetsToValidate.length == 0}
      disabled={streetsToValidate.length != 0}
    >
      Direcciones
    </Checkbox>
  </p>
  <EditorButton {user} action={'validar'}>
    <Button type="submit" name="status" value="LOCKED_FOR_VALIDATION" class="mr-4">
      Valídala
    </Button>
  </EditorButton>
{:else if status === 'INVALIDATED'}
  <p>need mor mapping</p>
{:else if status === 'MAPPED'}
  <p>
    Tarea <span class="text-success-500 font-bold">
      mapeada</span>{#if user && user.id === mapper?.id},
      otro usuario debe validarla.{/if}
  </p>
  {#if !user || (user?.id !== mapper?.id && !task.is_locked)}
    <EditorButton {user} action={'validar'}>
      <Button type="submit" name="status" value="LOCKED_FOR_VALIDATION" class="mr-4">
        Valídala
      </Button>
    </EditorButton>
  {/if}
{:else if status === 'VALIDATED'}
  <p>
    Tarea mapeada y <span class="text-success-500 font-bold">validada</span>.
  </p>
{/if}
