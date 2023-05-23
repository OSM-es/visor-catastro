<script>
  import L from 'leaflet'
  import { Button, Input } from 'flowbite-svelte'
  import { goto } from '$app/navigation'

  import { login } from '$lib/user'
  import Map from '$lib/Map.svelte'

  export let data

  let map
  let value = data.task.status
  let geoJsonData = data.task.content

  function setStyle(feature) {
    const style = { 
      weight: (feature?.properties?.tags || {})['building:part'] ? 1 : 2,
      fillOpacity: feature?.properties?.tags?.building ? 0.6 : 0.3,
      color: '#B22222',
    }
    return style
  }

  const entranceStyle = `
    background-color: #B22222;
    width: 0.8rem;
    height: 0.8rem;
    display: block;
    left: -0.4rem;
    top: -0.4rem;
    position: relative;
    border-radius: 0;
    border: 1px solid #FFFFFF`

  function createMarker(geoJsonPoint, latlng) {
    const icon = L.divIcon({
      className: "entrance",
      iconAnchor: [0, 0],
      labelAnchor: [-6, 0],
      popupAnchor: [0, -36],
      html: `<span style="${entranceStyle}" />`
    })
    return L.marker(latlng, { icon })
  }

  const geoJsonOptions = {
    style: setStyle,
    pointToLayer: createMarker,
  }

  function exit() {
    const zoom = map.getMap().getZoom() - 1
    const center = map.getMap().getCenter()
    const lat = center.lat.toFixed(4)
    const lng = center.lng.toFixed(4)

    goto(`/explore?map=${zoom}/${lat}/${lng}`)
  }
</script>

<div class="flex flex-col md:flex-row flex-grow">
  <div class="w-full flex-grow z-0">
    <Map
      bind:map
      geoJsonData={geoJsonData}
      geoJsonOptions={geoJsonOptions}
    />
  </div>
  <div class="md:max-w-md w-full flex-grow overflow-scroll px-4 pt-8 border-l-2 border-gray-200 dark:border-gray-600">
    <div class="h-full max-h-0">
      <div class="prose lg:prose-xl dark:prose-invert">
        <ul>
          <li>Catastro de {data.task.muncode}</li>
          <li>Referencia: {data.task.localId}</li>
          <li>Tipo: {data.task.type}</li>
          <li>Partes de edificio: {data.task.parts}</li>
          {#if data.user}
            <li>
              Estado:
              <Input type=number bind:value min=0 max=9 />
            </li>
            <Button on:click={exit} color="alternative">Cancelar</Button>
            <Button>Guardar</Button>
          {:else}
            <Button on:click={login}>Registrate para editar</Button>
          {/if}
        </ul>
      </div>
    </div>
  </div>
</div>
