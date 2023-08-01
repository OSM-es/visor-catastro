<script>
  import { Button, Badge, Checkbox, Listgroup, Radio } from 'flowbite-svelte'

	import { enhance } from '$app/forms'
  import { goto } from '$app/navigation'
  import { TASK_ACTION_TEXT } from '$lib/config'
  import { exploreCode } from '$lib/stores.js'
  import EditorButton from './EditorButton.svelte'

  export let title
  export let status
  export let mapper
  export let user
  export let task
  export let exitUrl

  const streets = task.streets.map(st => {
    st.href = `/explore/task/${task.id}/street/${st.cat_name}`
    return st
  })
  const streetsToValidate = task.streets?.filter(s => !s.validated) || []
  const canSelectImport = task.streets.length && !streetsToValidate.length && task.ad_status === task.bu_status

  let validationStatus = 'VALIDATED'
  let addresses = !['MAPPED', 'VALIDATED'].includes(task.ad_status) && streetsToValidate.length === 0
  let buildings = !['MAPPED', 'VALIDATED'].includes(task.bu_status)
  
  $: target = !task.lock || (title === 'buildings' ? task?.lock?.buildings : task?.lock?.addresses)
  $: isMapper = user && [mapper?.osm_id, mapper?.import_id].includes(user.id)
  $: needMapping = ['READY', 'INVALIDATED', 'NEED_UPDATE'].includes(status)

  function updateStatus() {
    return async ({ update }) => {
      await update({ reset: false })
      if (!task?.lock) exit()
    }
  }

  function exit() {
    const url = $exploreCode ? `/explore/${$exploreCode}` : '/explore'
    goto(`${url}?map=${exitUrl(-1)}`)
  }
</script>

{#if target}
  <form use:enhance={updateStatus} method="POST" action="?/task">
    {#if task.bu_status !== task.ad_status}
      <h4>{title === 'buildings' ? 'Edificios' : 'Direcciones'}</h4>
    {/if}

    {#if needMapping && !task.lock}
      <input name="addresses" value={addresses} hidden/>
      <input name="buildings" value={buildings} hidden/>
    {:else if task.lock}
      <input name="addresses" value={task.lock?.addresses} hidden/>
      <input name="buildings" value={task.lock?.buildings} hidden/>
    {:else}
      <input name="addresses" value={status === task.bu_status || title === 'addresses'} hidden/>
      <input name="buildings" value={status === task.bu_status || title === 'buildings'} hidden/>
    {/if}

    {#if task.lock && !task.isOwner}
      <p>
        Tarea
        <span class="font-bold text-danger-500">bloqueada</span> para
        {TASK_ACTION_TEXT[task.lock.text]} por otro usuario.
      </p>
    {:else if task.lock?.text === 'MAPPING'}
        <p>TODO: Aquí faltan enlaces para descargar el archivo de la tarea</p>
        <p>¿Esta tarea está completamente mapeada?</p>
        <EditorButton {user} {task} action={'guardar'}>
          <Button type="submit" name="status" value="MAPPED" class="mr-4">
            Si, guardar
          </Button>
        </EditorButton>
    {:else if task.lock?.text === 'VALIDATION'}
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
      <EditorButton {user} {task} action={'validar'}>
        <Button type="submit" class="mr-4">
          {validationStatus === 'VALIDATED' ? 'Validar' : 'Invalidar' }
        </Button>
      </EditorButton>
    {:else if needMapping}
      {#if status === 'INVALIDATED'}
        <p>Tarea marcada como que <span class="text-danger-500">necesita más mapeo</span>.</p>
      {:else if status === 'NEED_UPDATE'}
        <p>Tarea importada que necesita <span class="text-danger-500">actualizar</span>.</p>
      {/if}
      {#if task.streets?.length}
        {#if streetsToValidate.length}
          <h5>Nombres de calle:</h5>
          <Listgroup active items={streets} let:item class="not-prose">
            {item.cat_name}
            <Badge color={item.validated ? 'green' : 'red'}>
              {item.validated ? 'Confirmado' : 'Pendiente'}
            </Badge>
          </Listgroup>
          <p class="text-danger-500">
            Falta revisar {streetsToValidate.length}
            {streetsToValidate.length > 1 ? 'nombres' : 'nombre'}
            para poder importar direcciones.
          </p>
        {:else}
          <p>
            Revisión de 
            <a href={`/explore/task/${task.id}/street`}>nombres de calle</a>
            <span class="text-success-500">completa</span>.
          </p>
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
          class="mr-4 w-48"
          disabled={!buildings && !addresses}
        >
          Importar {buildings ? (addresses ? 'todo' : 'edificios') : (addresses ? 'direcciones' : '')}
        </Button>
      </EditorButton>
    {:else if status === 'MAPPED'}
      <p>
        Tarea <span class="text-success-500 font-bold">
          mapeada</span>{#if isMapper},
          otro usuario debe validarla.{/if}
      </p>
      {#if !isMapper && !task.lock}
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
    {#if title === 'addresses' || task.ad_status === task.bu_status || task.lock}
      {#if user && task.lock && task.isOwner}
        <Button type="submit" name="lock" value="UNLOCK" color="alternative">
          {task.lock.text === 'MAPPING' ? 'No, detener mapeo' : 'Detener validación'}
        </Button>
      {:else if !task.currentLock}
        <Button on:click={exit} color="alternative">Seleccionar otra tarea</Button>
      {/if}
    {/if}
  </form>
{/if}
