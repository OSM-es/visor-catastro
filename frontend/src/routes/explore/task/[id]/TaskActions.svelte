<script>
  import { Button, Badge, Checkbox, Listgroup, Radio } from 'flowbite-svelte'

  import { TASK_ACTION_TEXT } from '$lib/config'
  import EditorButton from './EditorButton.svelte'

  export let status
  export let user
  export let mapper
  export let task

  const streets = task.streets.map(st => {
    st.href = `/explore/${task.muncode}/street/${st.cat_name}`
    return st
  })
  const streetsToValidate = task.streets?.filter(s => !s.validated) || []
  const canSelectImport = task.streets.length && !streetsToValidate.length && task.ad_status == task.bu_status

  let validationStatus = 'VALIDATED'
  let addresses = !['MAPPED', 'VALIDATED'].includes(task.ad_status) && streetsToValidate.length === 0
  let buildings = !['MAPPED', 'VALIDATED'].includes(task.bu_status)
</script>

{#if status !== 'READY'}
  <input name="addresses" value={status === task.ad_status} hidden/>
  <input name="buildings" value={status === task.bu_status} hidden/>
{:else if !canSelectImport}
  <input name="addresses" value={addresses} hidden/>
  <input name="buildings" value={buildings} hidden/>
{/if}
{#if task.lock}
  {#if ![task.lock.user.osm_id, task.lock.user.import_id].includes(user?.id)}
    <p>
      Tarea
      <span class="font-bold text-danger-500">bloqueada</span> para
      {TASK_ACTION_TEXT[task.lock.text]} por otro usuario.
    </p>
  {:else if task.lock.text === 'MAPPING'}
    <p>TODO: Aquí faltan enlaces para descargar el archivo de la tarea</p>
    <p>¿Esta tarea está completamente mapeada?</p>
    <Button type="submit" name="status" value="MAPPED" class="mr-4">
      Si, guardar
    </Button>
  {:else if task.lock.text === 'VALIDATION'}
    <p>TODO: Aquí faltan enlaces para descargar el archivo de la tarea,
      y el área.
    </p>
    <p>¿Esta tarea está bien mapeada?</p>
    <div class="flex space-x-8 mb-8">
      <Radio
        type="radio"
        name="status"
        value="VALIDATED"
        bind:group={validationStatus}
      >
        Si
      </Radio>
      <Radio
        type="radio"
        name="status"
        value="INVALIDATED"
        bind:group={validationStatus}
      >
        No
    </Radio>
    </div>
    <Button type="submit" class="mr-4">
      {validationStatus === 'VALIDATED' ? 'Validar' : 'Invalidar' }
    </Button>
  {/if}
{:else if status === 'READY'}
  {#if task.streets?.length}
    <h5>Nombres de calle:</h5>
    <Listgroup active items={streets} let:item class="not-prose">
      {item.cat_name}
      <Badge color={item.validated ? 'green' : 'red'}>
        {item.validated ? 'Confirmado' : 'Pendiente'}
      </Badge>
    </Listgroup>
    {#if streetsToValidate.length}
      <p class="text-danger-500">
        Falta revisar {streetsToValidate.length}
        {streetsToValidate.length > 1 ? 'nombres' : 'nombre'}
        para poder importar direcciones.
      </p>
    {:else}
      <p class="text-success-500">Revisión de nombres de calle completa.</p>
    {/if}
  {/if}
  {#if canSelectImport}
    <p>
      Voy a importar
      <Checkbox name="buildings" value="true" bind:checked={buildings}>
        Edificios
      </Checkbox>
      <Checkbox name="addresses" value="true" bind:checked={addresses}>
        Direcciones
      </Checkbox>
    </p>
  {/if}
  <EditorButton {user} {task} action={'importar'}>
    <Button
      type="submit"
      name="lock"
      value="MAPPING"
      class="mr-4"
      disabled={!buildings && !addresses}
    >
      Importar {buildings ? (addresses ? 'todo' : 'edificios') : (addresses ? 'direcciones' : '')}
    </Button>
  </EditorButton>
{:else if status === 'INVALIDATED'}
  <p>TODO: need more mapping</p>
{:else if status === 'MAPPED'}
  <p>
    Tarea <span class="text-success-500 font-bold">
      mapeada</span>{#if user && [mapper.osm_id, mapper.import_id].includes(user?.id)},
      otro usuario debe validarla.{/if}
  </p>
  {#if !user || (![mapper.osm_id, mapper.import_id].includes(user?.id) && !task.lock)}
    <EditorButton {user} {task} action={'validar'}>
      <Button type="submit" name="lock" value="VALIDATION" class="mr-4">
        Valídala
      </Button>
    </EditorButton>
  {/if}
{:else if status === 'VALIDATED'}
  <p>
    Tarea mapeada y <span class="text-success-500 font-bold">validada</span>.
  </p>
{/if}
