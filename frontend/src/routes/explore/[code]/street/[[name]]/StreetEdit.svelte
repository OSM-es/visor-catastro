<script>
	import { getContext } from 'svelte'
  
  import { Button, ButtonGroup, Select } from 'flowbite-svelte'
  import { ArrowUturnLeft, Check, LockClosed, XMark } from 'svelte-heros-v2'

  import ResponsiveButton from '$lib/components/ResponsiveButton.svelte'

  export let osmStreets
  let  name, prev_name
  
  const btnClass = "!px-2 h-8 focus:!ring-0"
  const noImportar = 'No importar'
  const street = getContext('street')


  function osmStreetNames() {
    let names = osmStreets.features.map((feat) => (feat.properties?.tags?.name || ''))
    names = Array.from(new Set(names.filter((name) => (name ? true : false)))).sort()
    names = names.map((name) => ({ value: name, name }))
    names.push({value: '', name: noImportar})
    return names
  }

  function undoStreet() {
    name = prev_name
  }

  street.subscribe((street) => {
    name = street.validated ? street.name || '' : street.source === 'OSM' ? street.osm_name : ''
    prev_name = name
  })
</script>

<td>
  <input name="osm_name" value={$street.osm_name} hidden/>
  <ButtonGroup class="w-full" size="sm">
    <Select
      name="name"
      size="sm"
      items={osmStreetNames()}
      bind:value={name}
      placeholder=""
      class="ml-2 py-1.5 !rounded-r-sm disabled:opacity-50"
      disabled={$street.locked}
    />
    <Button
      class="!px-2.5 focus:!ring-0"
      on:click={() => (name = '')}
      disabled={$street.locked}
    >
      <XMark size=14/>
    </Button>
  </ButtonGroup>
</td>
<td class="px-2 py-0">
  {#if $street.locked}
    <LockClosed size=18/>
  {:else if $street.validated && name === prev_name}
    <ResponsiveButton 
      type="submit"
      title="Deshacer"
      name="validated"
      value="false"
      on:click={undoStreet}
      {btnClass}
    >
      <ArrowUturnLeft size=18/>
    </ResponsiveButton>
  {:else}
    <ResponsiveButton 
      type="submit"
      title="Confirmar"
      name="validated"
      value="true"
      {btnClass}
    >
      <Check size=18/>
    </ResponsiveButton>
  {/if}
</td>
