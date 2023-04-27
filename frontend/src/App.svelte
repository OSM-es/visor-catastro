<script>
  import L from "leaflet"
  import "leaflet/dist/leaflet.css"
  import places from "./results.json"

  let map, info, myLayer, messages = []
  const initialView = [40.463667, -3.74922]
  const zoomThreshold = 16

  const MESSAGES = {
    doZoom: "Haz zoom para poder editar",
    doTask: (muncode, localId) => `Borrador edición ${muncode} ${localId}`,
    fetchError: "Se ha producido un error al obtener el zoning.geojson",
  }

  const layerUrl = (id, label) => `http://localhost:8111/import?new_layer=true&url=https://catastro.openstreetmap.es/results/${id}/tasks/${label}.osm.gz`
  const geojsonUrl = (bounds) => `http://localhost/api/${bounds}`

  function createMap(container) {
    let m = L.map(container, { preferCanvas: true }).setView(
      initialView,
      9
    );

    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: `&copy;<a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a>`,
      maxZoom: 20,
      minZoom: 5,
    }).addTo(m);

    new L.Control.Zoom({ position: 'topright' }).addTo(m);
    addMessage(MESSAGES.doZoom)

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

  function onEachFeature({ properties: { muncode, localId } }, layer){
    layer.on("click", () => addMessage(MESSAGES.doTask(muncode, localId)))
    layer.on("mouseover", () => layer.setStyle({ fillColor: "orange", dashArray: "5,5" }))
    layer.on("mouseout", () => myLayer.resetStyle())
  }

  function handleMoveEnd({ target }) {
    const currentZoom = target.getZoom()

    info.update(currentZoom)

    if (currentZoom >= zoomThreshold) {
      const currentBounds = map.getBounds().toBBoxString()

      requestGeoJSON(currentBounds)
      removeMessage(MESSAGES.doZoom)
    } else {
      addMessage(MESSAGES.doZoom)
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

  function addMessage(item) {
    !messages.includes(item) && messages.push(item)
    messages = messages
  }
  
  function removeMessage(item) {
    messages.includes(item) && messages.splice(messages.indexOf(item), 1)
    messages = messages
  }

  function closeOverlay() {
    messages = []
  }

</script>

<svelte:window on:resize={resizeMap} />

<div class="map" style="height:100%;width:100%" use:mapAction />

{#if messages.length > 0}
  <div class="overlay">
    {#each messages as msg}
      <div class="message">{msg}</div>
    {/each}
    <button class="overlay-close" on:click={closeOverlay}>X</button>
  </div>
{/if}