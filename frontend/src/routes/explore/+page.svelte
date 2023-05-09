<script>
  import { onMount } from 'svelte'
  import { GeoJSON, LeafletMap, ScaleControl, TileLayer } from 'svelte-leafletjs'
  import { 
    PUBLIC_API_URL,
    PUBLIC_INITIAL_VIEW,
    PUBLIC_INITIAL_ZOOM,
  } from '$env/static/public'

  const center = PUBLIC_INITIAL_VIEW.split(',')
  const zoomThreshold = 16
  const geojsonUrl = (bounds) => `${PUBLIC_API_URL}${bounds}`

  let map, geoJsonData, selectedFeature
  let zoom = PUBLIC_INITIAL_ZOOM

  const attribution = `&copy; <a href="https://www.openstreetmap.org/copyright"` +
        `target="_blank">OpenStreetMap</a>`
  const mapOptions = { center, zoom }
  const tileUrl = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
  const tileLayerOptions = { minZoom: 5, maxZoom: 20, attribution }

  async function handleMoveEnd() {
    zoom = map.getMap().getZoom()
    if (zoom >= zoomThreshold) {
      const bounds = map.getMap().getBounds().toBBoxString()
      const response = await fetch(geojsonUrl(bounds))
      geoJsonData = await response.json()
    }
  }

  const scaleControlOptions = { maxWidth: 200, imperial: false }

  onMount(() => {
    map.getMap().zoomControl.setPosition('topright')
  })

  function setStyle(feature) {
    const colors = ['green', 'blue']
    return { fillColor: colors[feature.id % 2] }
  }

  const geoJsonOptions = {
    style: setStyle,
    onEachFeature: function(feature, layer) {
      layer.on("click", () => {
        console.info(feature)
        selectedFeature = feature
    })
      layer.on("mouseover", () => {
        layer.setStyle({ fillColor: "red", dashArray: "5,5" })
        selectedFeature = feature
      })
      layer.on("mouseout", () => {
        selectedFeature = null
        layer.setStyle(setStyle(feature))
      })
    },
  };
</script>

<div class="flex flex-col md:flex-row flex-grow">
  <div class="md:max-w-md w-full flex-grow px-4 mt-8">
    <div class="prose lg:prose-xl dark:prose-invert">
      {#if zoom < zoomThreshold}
      <p>
        Aquí se visalizará información de los proyectos de importación visibles
        en el mapa.
      </p>
      <p>
        Haz zoom para ver las tareas.
      </p>
      {:else}
        {#if selectedFeature}
        <ul>
          <li>Código de municipio: {selectedFeature.properties.muncode}</li>
          <li>Referencia: {selectedFeature.properties.localid}</li>
          <li>Partes de edificio: {selectedFeature.properties.parts}</li>
          <li>Estado: {selectedFeature.properties.status}</li>
        </ul>
        {:else}
        <p>
          Aquí se visualizará información de las tareas disponibles en el mapa.
        </p>
        <p>
          Selecciona una tarea.
        </p>
        {/if}
      {/if}
    </div>
  </div>
  <div class="w-full flex-grow z-0">
    <LeafletMap
      bind:this={map}
      options={mapOptions}
      events={['moveend']}
      on:moveend={handleMoveEnd}
    >
      <TileLayer url={tileUrl} options={tileLayerOptions}/>
      <ScaleControl position="bottomleft" options={scaleControlOptions}/>
      <GeoJSON data={geoJsonData} options={geoJsonOptions}/>
    </LeafletMap>
  </div>
</div>

<style>
:global(.control) {
  padding: 6px 8px;
  background: white;
  border: 2px solid rgba(0,0,0,0.2);
  background-clip: padding-box;
  border-radius: 5px;
  color: black;
  z-index: 9990 !important;
}
</style>