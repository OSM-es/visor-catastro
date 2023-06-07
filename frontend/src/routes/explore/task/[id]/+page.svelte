<script>
  import L from 'leaflet'
  import { Button, Input, Label } from 'flowbite-svelte'
  import { onMount } from 'svelte'
  import { goto } from '$app/navigation'
  import { GeoJSON } from 'svelte-leafletjs'
	import { enhance } from '$app/forms'

  import Map from '$lib/Map.svelte'
  import { STREET_COLORS } from '$lib/config'

  export let data

  $: isEditor = data.user?.role && data.user.role != 'READ_ONLY'

  let map, center, zoom, initialCenter, initialZoom, getGeoJSON, getUrl
  let value = data.task.status
  let buildings = data.task.buildings
  let parts = data.task.parts
  let fixmes = data.task?.fixmes
  
  let streets = buildings.features.reduce((streets, feat) => {
    const addr = getAddress(feat.properties.tags)
    if (addr && !streets.includes(addr)) {
      streets.push(addr)
    }
    return streets
  }, [])
  streets = data.task.streets.features.reduce((streets, feat) => {
    const addr = feat.properties.tags?.name
    if (addr && !streets.includes(addr)) {
      streets.push(addr)
    }
    return streets
  }, streets)

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

  function entranceIcon(address, housenumber) {
    const colorIndex = streets.indexOf(address) % STREET_COLORS.length
    const style = `
      background-color: ${STREET_COLORS[colorIndex]};
      display: ${housenumber ? 'inline' : 'block'};
      min-width: 0.8rem;
      min-height: 0.8rem;
      padding: 0 0.1rem 0 0.1rem;
      left: -0.4rem;
      top: -0.4rem;
      color: ${colorIndex > (STREET_COLORS.length / 2) ? 'black' : 'white'};
      position: relative;
      border: 1px solid ${colorIndex > (STREET_COLORS.length / 2) ? 'black' : 'white'};
    `
    return L.divIcon({
      className: "entrance",
      iconAnchor: [0, 0],
      labelAnchor: [-6, 0],
      popupAnchor: [0, -36],
      html: `<span style="${style}">${housenumber}</span`
    })
  }

  function centerMap(event) {
    const point = event.target.attributes.href.value.split(',')
    map.getMap().panTo([point[1], point[0]])
    event.preventDefault()
  }

  function getAddress(tags) {
    let address = ''
    if (tags['addr:street']) address = tags['addr:street']
    if (tags['addr:place']) address = tags['addr:place']
    return address
  }

  function streetStyle(feature) {
    const name = feature.properties.tags?.name
    const colorIndex = streets.indexOf(name) % STREET_COLORS.length
    const style = { 
      weight: 8,
      opacity: 0.6,
      fillOpacity: 0.3,
      color: name ? STREET_COLORS[colorIndex] : 'gray',
    }
    return style
  }

  function buildingStyle(feature) {
    const style = { 
      weight: (feature?.properties?.tags || {})['building:part'] ? 1 : 2,
      fillOpacity: feature?.properties?.tags?.building ? 0.6 : 0.3,
      color: '#B22222',
    }
    return style
  }

  function createFixme(geoJsonPoint, latlng) {
    let marker = L.marker(latlng, { icon: fixmeIcon })
    return marker.bindTooltip(geoJsonPoint.properties?.fixme)
  }

  function createAddress(geoJsonPoint, latlng) {
    const address = getAddress(geoJsonPoint.properties.tags)
    const housenumber = geoJsonPoint.properties.tags['addr:housenumber']
    let marker = L.marker(latlng, { icon: entranceIcon(address, housenumber) })
    return marker.bindTooltip(address + (housenumber ? ', ' + housenumber : ''))
  }

  const fixmeOptions = {pointToLayer: createFixme }

  const streetOptions = {
    style: streetStyle,
    onEachFeature: function(feature, layer) {
      const name = feature.properties.tags?.name
      if (name) layer.bindTooltip(name, { sticky: true })
    }
  }

  const buildingOptions = {
    style: buildingStyle,
    pointToLayer: createAddress,
    onEachFeature: function(feature, layer) {
      const tags = JSON.stringify(feature.properties.tags, null, '<br/>')?.replace(/[\"{}]/g, '')
      if (tags && !tags.includes('building:part')) layer.bindPopup(tags)
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
      <GeoJSON data={data.task.streets} options={streetOptions}/>
      <GeoJSON data={parts} options={buildingOptions}/>
      <GeoJSON data={buildings} options={buildingOptions} bind:getGeoJSON/>
      {#if fixmes}<GeoJSON data={fixmes} options={fixmeOptions}/>{/if}
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
        {#if fixmes}
          <p>Anotaciones:</p>
          {#each fixmes?.features as fixme}
            <ol>
              <li>
                <a href="{fixme.geometry.coordinates}" on:click={centerMap}>
                  {fixme.properties.fixme}
                </a>
              </li>
            </ol>
          {/each}
        {/if}
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
