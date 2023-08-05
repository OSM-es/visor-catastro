<script>
  import { Button, Badge, Checkbox, Listgroup, Radio } from 'flowbite-svelte'

	import { enhance } from '$app/forms'
  import { goto } from '$app/navigation'
  import { t } from '$lib/translations'
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
    return async ({ result, update }) => {
      await update({ reset: false })
      if (result.type === 'success' && !task?.lock) exit()
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
      <h4 class="capitalize">{title === 'buildings' ? $t('explore.buildings') : $t('explore.addresses')}</h4>
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
      <p>{@html $t('task.islocked', { lock: $t('task.' + task.lock.text) })}</p>
    {:else if task.lock?.text === 'MAPPING'}
        <p>TODO: Aquí faltan enlaces para descargar el archivo de la tarea</p>
        <p>{$t('task.ismapped')}</p>
        <EditorButton {user} {task} action={$t('common.save')}>
          <Button type="submit" name="status" value="MAPPED" class="mr-4">
            {$t('task.save')}
          </Button>
        </EditorButton>
    {:else if task.lock?.text === 'VALIDATION'}
      <p>TODO: Aquí faltan enlaces para descargar el archivo de la tarea,
        y el área.
      </p>
      <p>{$t('task.isvalid')}</p>
      <div class="flex space-x-8 mb-8">
        <Radio
          type="radio"
          name="status"
          value="VALIDATED"
          bind:group={validationStatus}
        >
          {$t('common.yes')}
        </Radio>
        <Radio
          type="radio"
          name="status"
          value="INVALIDATED"
          bind:group={validationStatus}
        >
          {$t('common.no')}
      </Radio>
      </div>
      <EditorButton {user} {task} action={$t('task.VALIDATION')}>
        <Button type="submit" class="mr-4">
          {validationStatus === 'VALIDATED' ? $t('task.validate') : $t('task.invalidate') }
        </Button>
      </EditorButton>
    {:else if needMapping}
      {#if status === 'INVALIDATED'}
        {@html $t('task.invalidatedtext')}
      {:else if status === 'NEED_UPDATE'}
        {@html $t('task.updatetext')}
    {/if}
      {#if task.streets?.length}
        {#if streetsToValidate.length}
          <h5>{$t('task.streets')}</h5>
          <Listgroup active items={streets} let:item class="not-prose">
            {item.cat_name}
            <Badge color={item.validated ? 'green' : 'red'}>
              {item.validated ? $t('task.confirmed') : $t('task.pending')}
            </Badge>
          </Listgroup>
          <p class="text-danger-500">
            {$t('task.pendingstreets', { streets: streetsToValidate.length})}
          </p>
        {:else}
          <p>
            {@html $t('task.streetscompleted', { url: `/explore/task/${task.id}/street` })}
        </p>
        {/if}
      {/if}
      {#if canSelectImport}
        <p class="capitalize">
          {$t('task.willimport')}
          <Checkbox name="buildings" value="true" bind:checked={buildings}>
            {$t('explore.buildings')}
          </Checkbox>
          <Checkbox name="addresses" value="true" bind:checked={addresses}>
            {$t('explore.addresses')}
          </Checkbox>
        </p>
      {/if}
      <EditorButton {user} {task} action={$t('task.MAPPING')}>
        <Button
          type="submit"
          name="lock"
          value="MAPPING"
          class="mr-4 w-48"
          disabled={!buildings && !addresses}
        >
          {buildings ? (addresses ? $t('task.mapall') : $t('task.mapbuildings')) : (addresses ? $t('task.mapaddresses') : '')}
        </Button>
      </EditorButton>
    {:else if status === 'MAPPED'}
      <p>
        {@html $t('task.mappedtext')}{#if isMapper},
          {$t('task.needvalidation')}{/if}
      </p>
      {#if !isMapper && !task.lock}
        <EditorButton {user} {task} action={$t('task.VALIDATION')}>
          <Button type="submit" name="lock" value="VALIDATION" class="mr-4">
            {$t('task.validateit')}
          </Button>
        </EditorButton>
      {/if}
    {:else if status === 'VALIDATED'}
      <p>
        {@html $t('task.validatedtext')}
      </p>
    {/if}
    {#if title === 'addresses' || task.ad_status === task.bu_status || task.lock}
      {#if user && task.lock && task.isOwner}
        <Button type="submit" name="lock" value="UNLOCK" color="alternative">
          {task.lock.text === 'MAPPING' ? $t('task.stopmapping') : $t('task.stopvalidation')}
        </Button>
      {:else if !task.currentLock}
        <Button on:click={exit} color="alternative">{$t('task.selectanother')}</Button>
      {/if}
    {/if}
  </form>
{/if}
