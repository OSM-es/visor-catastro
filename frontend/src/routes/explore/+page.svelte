<script>
  import "leaflet/dist/leaflet.css"
  import { GeoJSON, LeafletMap, ScaleControl, TileLayer } from 'svelte-leafletjs'
  import { 
    PUBLIC_API_URL,
    PUBLIC_INITIAL_VIEW,
    PUBLIC_INITIAL_ZOOM,
  } from '$env/static/public'

  const center = PUBLIC_INITIAL_VIEW.split(',')
  const zoomThreshold = 16
  const geojsonUrl = (bounds) => `${PUBLIC_API_URL}/tasks?bounds=${bounds}`

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
  <div class="md:max-w-md w-full flex-grow overflow-scroll px-4 pt-8 border-l-2 border-gray-200 dark:border-gray-600">
    <div class="h-full max-h-0 prose lg:prose-xl dark:prose-invert">
      {#if zoom < zoomThreshold}
        <p>
          Aquí se visalizará información de los proyectos de importación visibles
          en el mapa.
        </p>
        <p>Haz zoom al nivel de escala 300 metros para ver las tareas.</p>
        <p>
          Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Egestas congue quisque egestas diam in arcu cursus euismod. Nulla pellentesque dignissim enim sit amet venenatis. Adipiscing elit ut aliquam purus sit amet luctus. Turpis massa sed elementum tempus egestas sed sed risus pretium. Egestas integer eget aliquet nibh. Odio eu feugiat pretium nibh ipsum consequat nisl. Nibh praesent tristique magna sit amet. Vitae auctor eu augue ut lectus arcu bibendum at. Ultricies leo integer malesuada nunc vel risus commodo viverra. Diam in arcu cursus euismod quis viverra nibh cras. Semper auctor neque vitae tempus quam pellentesque nec nam aliquam. Tempor nec feugiat nisl pretium fusce id velit ut tortor. Tellus elementum sagittis vitae et leo duis ut. Ante metus dictum at tempor commodo ullamcorper a. Tortor pretium viverra suspendisse potenti nullam ac tortor vitae. Donec adipiscing tristique risus nec.
        </p>
        <p>
          Amet consectetur adipiscing elit pellentesque habitant morbi tristique senectus et. Netus et malesuada fames ac turpis egestas sed tempus urna. Scelerisque varius morbi enim nunc. Ut morbi tincidunt augue interdum velit euismod in pellentesque. Posuere morbi leo urna molestie at. A arcu cursus vitae congue. Pretium fusce id velit ut tortor pretium. Ornare quam viverra orci sagittis eu volutpat odio facilisis mauris. Risus commodo viverra maecenas accumsan lacus. Blandit turpis cursus in hac habitasse platea. Sed lectus vestibulum mattis ullamcorper. Potenti nullam ac tortor vitae purus faucibus ornare suspendisse. Maecenas pharetra convallis posuere morbi leo urna molestie.
        </p>
        <p>
          Sed turpis tincidunt id aliquet risus. Id velit ut tortor pretium. Ipsum faucibus vitae aliquet nec ullamcorper sit amet risus. Fermentum iaculis eu non diam phasellus vestibulum lorem sed. Sagittis vitae et leo duis. Tempus quam pellentesque nec nam aliquam sem. Elit ut aliquam purus sit amet luctus venenatis. Rhoncus est pellentesque elit ullamcorper dignissim cras tincidunt. Eget nulla facilisi etiam dignissim diam quis enim. Eu feugiat pretium nibh ipsum consequat. Mauris commodo quis imperdiet massa tincidunt nunc pulvinar sapien. Arcu non odio euismod lacinia at quis risus.
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