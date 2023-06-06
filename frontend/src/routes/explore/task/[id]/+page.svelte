<script>
  import L from 'leaflet'
  import { Button, Input, Label } from 'flowbite-svelte'
  import { onMount } from 'svelte'
  import { goto } from '$app/navigation'
  import { GeoJSON } from 'svelte-leafletjs'
	import { enhance } from '$app/forms'

  import Map from '$lib/Map.svelte'

  export let data

  $: isEditor = data.user?.role && data.user.role != 'READ_ONLY'

  let map, center, zoom, initialCenter, initialZoom, getGeoJSON, getUrl
  let value = data.task.status
  let buildings = data.task.buildings
  let parts = data.task.parts
  let fixmes = data.task?.fixmes

  const entranceStyle = `
    background-color: #006400;
    display: {text ? inline : block};
    min-width: 0.8rem;
    min-height: 0.8rem;
    padding: 0 0.1rem 0 0.1rem;
    left: -0.4rem;
    top: -0.4rem;
    color: white;
    position: relative;
    border: 1px solid #FFFFFF;
  `

  const entranceIcon = (housenumber) => L.divIcon({
    className: "entrance",
    iconAnchor: [0, 0],
    labelAnchor: [-6, 0],
    popupAnchor: [0, -36],
    html: `<span style="${entranceStyle}">${housenumber}</span`
  })

  const fixmeTextStyle = `
    position: absolute;
    top: -35px;
    left: -4px;
    color: white;
    font-size: 1.5rem;
    font-weight: bold;
  `

  const fixmeIconStyle = `
    width: 30px;
    height: 30px;
    border-radius: 50% 50% 50% 0;
    background: red;
    position: absolute;
    transform: rotate(-45deg);
    left: -15px;
    top: -35px;
    border: 2px solid #FFFFFF;
  `

  const fixmeIcon = L.divIcon({
    className: "fixme",
    iconAnchor: [0, 0],
    labelAnchor: [-6, 0],
    popupAnchor: [0, -36],
    tooltipAnchor: [15, -20],
    html: `<span style="${fixmeIconStyle}"></span><span style="${fixmeTextStyle}">!</span>`
  })

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
    let tooltip, marker
    if (geoJsonPoint.properties?.fixme) {
      tooltip = geoJsonPoint.properties?.fixme
      marker = L.marker(latlng, { icon: fixmeIcon })
    } else {
      const text = geoJsonPoint.properties.tags['addr:housenumber']
      tooltip = getAddress(geoJsonPoint.properties.tags)
      marker = L.marker(latlng, { icon: entranceIcon(text) })
    }
    marker.bindTooltip(tooltip)
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
    goto('/learn/' + (data?.user?.tutorial ? data.user.tutorial.next : 'login'))
  }

  onMount(() => {
    map.getMap().fitBounds(getGeoJSON().getBounds())
    initialZoom = zoom
    initialCenter = center
  })
</script>

<div class="flex flex-col md:flex-row flex-grow">
  <div class="w-full flex-grow z-0">
    <Map bind:map bind:center bind:zoom bind:getUrl minZoom=15>
      <GeoJSON data={parts} options={geoJsonOptions}/>
      <GeoJSON data={buildings} options={geoJsonOptions} bind:getGeoJSON/>
      {#if fixmes}<GeoJSON data={fixmes} options={geoJsonOptions}/>{/if}
    </Map>
  </div>
  <div class="md:max-w-md w-full flex-grow overflow-scroll px-4 pt-8 border-l-2 border-gray-200 dark:border-gray-600">
    <div class="h-full max-h-0">
      <div class="prose dark:prose-invert">
        <ul>
          <li>Catastro de {data.task.muncode}</li>
          <li>Referencia: {data.task.localId}</li>
          <li>Tipo: {data.task.type}</li>
          <li>Partes de edificio: {data.task.parts.features.length}</li>
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
