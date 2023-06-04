<script>
  import L from 'leaflet'
  import { Button, Input, Label } from 'flowbite-svelte'
  import { onMount } from 'svelte'
  import { goto } from '$app/navigation'
  import { GeoJSON } from 'svelte-leafletjs'
	import { enhance } from '$app/forms'

  import Map from '$lib/Map.svelte'

  export let data

  const isEditor = data.user?.user && data.user.user.role != 'READ_ONLY'

  let map, center, zoom, initialCenter, initialZoom, getGeoJSON, getUrl
  let value = data.task.status
  let buildings = data.task.buildings
  let parts = data.task.parts

  function getAddress(tags) {
    let address = ''
    if (tags['addr:street']) address = tags['addr:street']
    if (tags['addr:place']) address = tags['addr:place']
    if (tags['addr:housenumber']) address += (', ' + tags['addr:housenumber'])
    return address
  }

  function setStyle(feature) {
    const address = getAddress(feature?.properties?.tags || {})
    const style = { 
      weight: (feature?.properties?.tags || {})['building:part'] ? 1 : 2,
      fillOpacity: feature?.properties?.tags?.building ? 0.6 : 0.3,
      color: address ? '#006400' : '#B22222',
    }
    return style
  }

  function createMarker(geoJsonPoint, latlng) {
    const address = getAddress(geoJsonPoint.properties.tags)
    const housenumber = geoJsonPoint.properties.tags['addr:housenumber']
    const entranceStyle = `
      background-color: #006400;
      display: {housenumber ? inline : block};
      min-width: 0.8rem;
      min-height: 0.8rem;
      padding: 0 0.1rem 0 0.1rem;
      left: -0.4rem;
      top: -0.4rem;
      color: white;
      position: relative;
      border: 1px solid #FFFFFF`
    const icon = L.divIcon({
      className: "entrance",
      iconAnchor: [0, 0],
      labelAnchor: [-6, 0],
      popupAnchor: [0, -36],
      html: `<span style="${entranceStyle}">${housenumber}</span`
    })
    const marker = L.marker(latlng, { icon })
    marker.bindTooltip(address)
    return marker
  }

  const geoJsonOptions = {
    style: setStyle,
    pointToLayer: createMarker,
    onEachFeature: function(feature, layer) {
      const tags = JSON.stringify(feature.properties.tags, null, '<br/>')?.replace(/[\"{}]/g, '')
      const address = getAddress(feature?.properties?.tags || {})
      if (tags && !tags.includes('building:part')) layer.bindPopup(tags)
      if (address) layer.bindTooltip(address)
    },
  }

  function exit() {
    goto(`/explore?map=${getUrl(-1)}`)
  }

  const updateStatus = () => {
    return async ({ update }) => {
      await update()
      exit()
    }
  }

  function doTutorial() {
    goto('/learn/login')
  }

  onMount(() => {
    map.getMap().fitBounds(getGeoJSON().getBounds())
    initialZoom = zoom
    initialCenter = center
  })
</script>

<div class="flex flex-col md:flex-row flex-grow">
  <div class="w-full flex-grow z-0">
    <Map bind:map bind:center bind:zoom bind:getUrl>
      <GeoJSON data={parts} options={geoJsonOptions}/>
      <GeoJSON data={buildings} options={geoJsonOptions} bind:getGeoJSON/>
    </Map>
  </div>
  <div class="md:max-w-md w-full flex-grow overflow-scroll px-4 pt-8 border-l-2 border-gray-200 dark:border-gray-600">
    <div class="h-full max-h-0">
      <div class="prose lg:prose-xl dark:prose-invert">
        <ul>
          <li>Catastro de {data.task.muncode}</li>
          <li>Referencia: {data.task.localId}</li>
          <li>Tipo: {data.task.type}</li>
          <li>Partes de edificio: {data.task.parts}</li>
        </ul>
        <form use:enhance={updateStatus} method="POST">
          <Label for="status">Estado:</Label>
          <Input id="status" name="status" type=number bind:value min=0 max=9 disabled={!isEditor} />
          <Button on:click={exit} color="alternative">Cancelar</Button>
          {#if isEditor}
            <Button type="submit">Guardar</Button>
          {:else}
            <Button on:click={doTutorial}>Completa el tutorial para editar</Button>
          {/if}
        </form>
      </div>
    </div>
  </div>
</div>
