<script>
	import { getContext } from 'svelte'
  
  import { Button, ButtonGroup, Select } from 'flowbite-svelte'
  import { ArrowUturnLeft, Check, XMark } from 'svelte-heros-v2'

  import { login } from '$lib/user'
  import ResponsiveButton from '$lib/components/ResponsiveButton.svelte'
  
  export let data
  export let id = undefined

  let  name, prev_name
  
  const btnClass = "!px-2 h-8 focus:!ring-0"
  const noImportar = 'No importar'
  const street = getContext('street')


  function osmStreetNames() {
    let names = data.osmStreets.features.map((feat) => (feat.properties?.tags?.name || ''))
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

<tr {id} class="bg-amber-400 text-gray-900 dark:text-white font-medium">
  <td class="px-4 py-2 w-1/3">
    <input name="mun_code" value={$street.mun_code} hidden/>
    <input name="cat_name" value={$street.cat_name} hidden/>
    {$street.cat_name}
  </td>
  {#if data?.user}
    <td>
      <input name="osm_name" value={$street.osm_name} hidden/>
      <ButtonGroup class="w-full" size="sm">
        <Select
          name="name"
          size="sm"
          items={osmStreetNames()}
          bind:value={name}
          placeholder=""
          class="ml-2 py-1.5 !rounded-r-sm"
        />
        <Button class="!px-2.5 focus:!ring-0" on:click={() => (name = '')}>
          <XMark size=14/>
        </Button>
      </ButtonGroup>
    </td>
    <td class="px-2 py-0 w-1/6">
      {#if $street.validated && name === prev_name}
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
  {:else}
    <td>
      <Button size="sm" on:click={login} class={btnClass}>Registrate para editar</Button>
    </td>
    <td class="px-4 py-0 w-1/6">
      {#if $street.validated}<Check size=18/>{/if}
    </td>
  {/if}
  <td class="px-4 py-2 w-1/6">
    <input name="source" value={$street.source} hidden/>
    {$street.source}
  </td>
</tr>