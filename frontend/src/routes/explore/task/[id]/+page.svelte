<script>
  // import 'leaflet/dist/leaflet.css'
  // import { GeoJSON, LeafletMap, ScaleControl, TileLayer } from 'svelte-leafletjs'
  import { Button, Input } from 'flowbite-svelte'
  // import { onMount } from 'svelte'

  import { login } from '$lib/user'
  import Map from '$lib/Map.svelte'

  export let data

  let value = data.task.status
  let geoJsonData = data.task.content
  
  // const attribution = `&copy; <a href="https://www.openstreetmap.org/copyright"` +
  //       `target="_blank">OpenStreetMap</a>`
  // const tileUrl = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
  // const tileLayerOptions = { minZoom: 5, maxZoom: 19, attribution }
  // const scaleControlOptions = { maxWidth: 200, imperial: false }

  // onMount(() => {
  //   console.info(2)
  //   const bounds = getGeoJSON().getBounds()
  //   console.info(bounds)
  //   getMap().fitBounds(bounds)
  // })
</script>

<div class="flex flex-col md:flex-row flex-grow">
  <div class="w-full flex-grow z-0">
    <Map geoJsonData={geoJsonData}/>
    <!-- LeafletMap bind:this={map} bind:getMap>
      <TileLayer url={tileUrl} options={tileLayerOptions}/>
      <ScaleControl position="bottomleft" options={scaleControlOptions}/>
      <GeoJSON data={geoJsonData} bind:getGeoJSON/>
    </LeafletMap -->
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
            <Button href="/explore" color="alternative">Cancelar</Button>
            <Button>Guardar</Button>
          {:else}
            <Button on:click={login}>Registrate para editar</Button>
          {/if}
        </ul>
      </div>
    </div>
  </div>
</div>
