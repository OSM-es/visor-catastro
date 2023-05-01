<script>
  import L from "leaflet"
  import "leaflet/dist/leaflet.css"
  import { Alert } from 'flowbite-svelte';
  
  let map, info, myLayer
  const initialView = [[40.463667, -3.74922], 9]
  const zoomThreshold = 16
  const geojsonUrl = (bounds) => `http://localhost/api/${bounds}`

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

  function onEachFeature({ properties: { muncode, localid } }, layer){
    // TODO layer.on("click", () => addMessage(MESSAGES.doTask(muncode, localid)))
    layer.on("mouseover", () => layer.setStyle({ fillColor: "orange", dashArray: "5,5" }))
    layer.on("mouseout", () => myLayer.resetStyle())
  }

  function handleMoveEnd({ target }) {
    const currentZoom = target.getZoom()

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
      Bienvenid@ a la herramienta de gestión de la importación del
      Catastro Español a OpenStreetMap. 
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