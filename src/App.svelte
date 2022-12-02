<script>
  import L from "leaflet";
  import "leaflet/dist/leaflet.css";
  import places from "./results.json"

  let map, info;
  const initialView = [40.463667, -3.74922];

  const layerUrl = (id, label) => `http://localhost:8111/import?new_layer=true&url=https://catastro.openstreetmap.es/results/${id}/tasks/${label}.osm.gz`
  const geojsonUrl = (id) => `https://visor-catastro.cartobase.es/results/${id}/zoning.geojson`
  const cachedFeatures = new Map()

  function createMap(container) {
    let m = L.map(container, { preferCanvas: true }).setView(
      initialView,
      9
    );
    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: `&copy;<a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a>,
          &copy;<a href="https://carto.com/attributions" target="_blank">CARTO</a>`,
      maxZoom: 20,
      minZoom: 5,
    }).addTo(m);

    return m;
  }

  function mapAction(container) {
    map = createMap(container);

    map.on("moveend", handleMoveEnd)

    info.addTo(map);

    return {
      destroy: () => {
        map.remove();
        map = null;
      },
    };
  }

  async function requestGeoJSON(ids){
    const responses = await Promise.all(ids.map(id => fetch(geojsonUrl(id)).then(r => r.json())))
    responses.map((res, ix) => {
      const feature = L.geoJSON(res, { onEachFeature })

      feature.addTo(map)
      cachedFeatures.set(ids[ix], feature)
    })
  }

  function onEachFeature({ properties: { muncode, localId } }, layer){
    layer.on("click", () => window.open(layerUrl(muncode, localId)))
    layer.on("mouseover", () => layer.setStyle({ fillColor: "orange", dashArray: "5,5" }))
    layer.on("mouseout", () => cachedFeatures.get(muncode).resetStyle())
  }

  function handleMoveEnd({ target }) {
    const currentZoom = target.getZoom()

    info.update(currentZoom)

    if (currentZoom > 12) {
      const currentBounds = map.getBounds()
      // get the items in the bounding box
      const zonings = Object.entries(places).filter(([, coords]) => currentBounds.contains(L.latLng(...coords))).map(([key]) => key)
      // request only new items
      const notCached = zonings.filter(x => !cachedFeatures.has(x))
      
      if (notCached.length) {
        requestGeoJSON(notCached)
      }
    }
  }

  function resizeMap() {
    if (map) {
      map.invalidateSize();
    }
  }

  info = L.control({position: 'topleft'})
  info.onAdd = function () {
    this._div = L.DomUtil.create('div', "control");
    this.update()
    return this._div;
  };

  info.update = function (value) {
    this._div.innerHTML = `Zoom: ${value || map.getZoom()}`;
  };

</script>

<svelte:window on:resize={resizeMap} />

<div class="map" style="height:100%;width:100%" use:mapAction />