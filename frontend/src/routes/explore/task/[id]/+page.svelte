<script>
  import L from 'leaflet'
  import { Button, Input, Label } from 'flowbite-svelte'
  import { onMount } from 'svelte'
  import { goto } from '$app/navigation'
  import { GeoJSON } from 'svelte-leafletjs'
	import { enhance } from '$app/forms'

  import Map from '$lib/Map.svelte'
  import FotosFachada from './FotosFachada.svelte'
  import { STREET_COLORS } from '$lib/config'
  
  export let data

  const urlFF = 'http://ovc.catastro.meh.es/OVCServWeb/OVCWcfLibres/OVCFotoFachada.svc/RecuperarFotoFachadaGet?ReferenciaCatastral='

  let map, center, zoom, initialCenter, initialZoom, getGeoJSON, getUrl
  let value = data.task.status
  let buildings = data.task.buildings
  let fixmes = data.task?.fixmes
  let scrollImage, viewImage
  
  $: isEditor = data.user?.role && data.user.role != 'READ_ONLY'
  $: console.info(data)
  
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
    const colorIndex = data.task.streetNames.indexOf(address) % STREET_COLORS.length
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
      if (tags && !tags.includes('building:part')) {
        const ref = feature.properties.tags.ref
        layer.bindPopup(`<a href="?ref=${ref}"><img src="${urlFF}${ref}"/></a>` + tags)
        layer.on('popupopen', onPoupOpen)
        layer.on('popupclose', onPopupClose)
        feature.layer = layer
      }
    },
  }


  function centerMap(event) {
    const point = event.target.attributes.href.value.split(',')
    map.getMap().panTo([point[1], point[0]])
    event.preventDefault()
  }

  function getAddress(tags) {
    return tags['addr:street'] || tags['addr:place'] || ''
  }

  function streetStyle(feature) {
    const name = feature.properties.tags?.name
    const colorIndex = data.task.streetNames.indexOf(name) % STREET_COLORS.length
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

  function onPoupOpen({ target }) {
    scrollImage = target.feature.properties?.tags?.ref
  }

  function onPopupClose() {
    goto(document.location.pathname)
  }

  function showBuilding({ detail }) {
    const ref = detail
    const building = buildings.features.find(building => building.properties.tags?.ref === ref)
    building.layer.openPopup()
  }

  function dataChange(data) {
    viewImage = data.imageRef
  }

  function exit() {
    goto(`/explore?map=${getUrl(-1)}`)
  }

  function updateStatus() {
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
    scrollImage = data.imageRef
    viewImage = data.imageRef
  })
</script>

<div class="flex flex-col md:flex-row flex-grow">
  <div class="w-full flex-grow z-0">
    <Map bind:map bind:center bind:zoom bind:getUrl minZoom=15>
      <GeoJSON data={data.task.streets} options={streetOptions}/>
      <GeoJSON data={data.task.parts} options={buildingOptions}/>
      <GeoJSON data={data.task.buildings} options={buildingOptions} bind:getGeoJSON/>
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
                <a
                  href="{fixme.geometry.coordinates}"
                  on:click={centerMap}
                  data-sveltekit-preload-data="off"
                >
                  {fixme.properties.fixme}
                </a>
              </li>
            </ol>
          {/each}
        {/if}
        <form use:enhance={updateStatus} method="POST" class="mb-4">
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
      {viewImage}
      {data.imageRef}
      <FotosFachada
        images={data.task.images}
        on:showBuilding={showBuilding}
        bind:scrollImage 
        bind:viewImage
      />
    </div>
  </div>
</div>
