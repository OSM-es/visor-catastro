<script>
  import L from "leaflet"
  import "leaflet/dist/leaflet.css"
  import { PUBLIC_API_URL, PUBLIC_INITIAL_VIEW } from '$env/static/public'

  const initialView = [
    PUBLIC_INITIAL_VIEW.split(',', 2),
    PUBLIC_INITIAL_VIEW.split(',')[2]
  ]
  const zoomThreshold = 16
  const geojsonUrl = (bounds) => `${PUBLIC_API_URL}${bounds}`

  let map, info, myLayer, selectedTask
  let currentZoom = initialView[1]

  function createMap(container) {
    let m = L.map(container, { preferCanvas: true }).setView(...initialView)
    let attribution = `&copy; <a href="https://www.openstreetmap.org/copyright"` +
      `target="_blank">OpenStreetMap</a>`

    m.attributionControl.setPrefix(false)
    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution,
      maxZoom: 20,
      minZoom: 5,
    }).addTo(m);

    return m;
  }

  function mapAction(container) {
    map = createMap(container)

    map.on("moveend", handleMoveEnd)

    info.addTo(map)

    return {
      destroy: () => {
        map.remove();
        map = null;
      },
    };
  }

  async function requestGeoJSON(bounds){
    const response = await fetch(geojsonUrl(bounds)).then(r => r.json())

    if (myLayer !== undefined) {
      map.removeLayer(myLayer)
    }
    myLayer = L.geoJSON(response.features, { onEachFeature })
    myLayer.addTo(map)
  }

  function onEachFeature({ properties }, layer){
    layer.on("click", () => selectedTask = properties)
    layer.on("mouseover", () => layer.setStyle({ fillColor: "orange", dashArray: "5,5" }))
    layer.on("mouseout", () => myLayer.resetStyle())
  }

  function handleMoveEnd({ target }) {
    currentZoom = target.getZoom()

    info.update(currentZoom)

    if (currentZoom >= zoomThreshold) {
      const currentBounds = map.getBounds().toBBoxString()

      requestGeoJSON(currentBounds)
    }
  }

  function resizeMap() {
    if (map) {
      map.invalidateSize()
    }
  }

  info = L.control({position: 'topleft'})
  info.onAdd = function () {
    this._div = L.DomUtil.create('div', "control")
    this.update()
    return this._div
  };

  info.update = function (value) {
    this._div.innerHTML = `Zoom: ${value || map.getZoom()}`;
  };

</script>

<svelte:window on:resize={resizeMap} />

<div class="flex flex-col md:flex-row flex-grow">
  <div class="md:max-w-md w-full flex-grow px-4 mt-8">
    <div class="prose lg:prose-xl dark:prose-invert">
      {#if currentZoom < zoomThreshold}
      <p>
        Aquí se visalizará información de los proyectos de importación visibles
        en el mapa.
      </p>
      <p>
        Haz zoom para ver las tareas.
      </p>
      {:else}
        {#if selectedTask}
        <ul>
          <li>Código de municipio: {selectedTask.muncode}</li>
          <li>Referencia: {selectedTask.localid}</li>
          <li>Partes de edificio: {selectedTask.parts}</li>
          <li>Estado: {selectedTask.status}</li>
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
  <div class="map w-full flex-grow z-0" use:mapAction />
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