<script>
  import { Button, ButtonGroup, Select } from 'flowbite-svelte'
  import { ArrowUturnLeft, Check, XMark } from 'svelte-heros-v2'

  import { page } from '$app/stores'

  import { login } from '$lib/user'
  import ResponsiveButton from '$lib/components/ResponsiveButton.svelte'
  
  export let data
  export let id = undefined

  let  name, prev_name
  
  const btnClass = "!px-2 h-8 focus:!ring-0"
  const noImportar = 'No importar'


  function osmStreetNames() {
    let names = data.osmStreets.features.map((feat) => (feat.properties?.tags?.name || ''))
    names = Array.from(new Set(names.filter((name) => (name ? true : false)))).sort()
    names = names.map((name) => ({ value: name, name }))
    names.push({value: '', name: noImportar})
    return names
  }

  page.subscribe(() => {
    name = data.validated ? data.name || '' : (data.source === 'OSM' ? data.osm_name : '')
    prev_name = name
  })
</script>

<tr {id} class="!bg-amber-400">
  <td class="px-4 py-2 w-1/3">
    <input name="mun_code" value={data.mun_code} hidden/>
    <input name="cat_name" value={data.cat_name} hidden/>
    {data.cat_name} {data.validated} {name} {prev_name}
  </td>
  {#if data?.user}
    <td>
      <input name="osm_name" value={data.osm_name} hidden/>
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
      {#if data.validated && name === prev_name}
        <ResponsiveButton 
          type="submit" title="Deshacer" name="validated" value="false" {btnClass}
        >
          <ArrowUturnLeft size=18/>
        </ResponsiveButton>
      {:else}
        <ResponsiveButton 
          type="submit" title="Confirmar" name="validated" value="true" {btnClass}
        >
          <Check size=18/>
        </ResponsiveButton>
      {/if}
    </td>
  {:else}
    <td>
      <Button size="sm" on:click={login}>Registrate para editar</Button>
    </td>
    <td class="px-4 py-0 w-1/6">
      {#if data.validated}<Check size=18/>{/if}
    </td>
  {/if}
  <td class="px-4 py-2 w-1/6">
    <input name="source" value={data.source} hidden/>
    {data.source}
  </td>
</tr>