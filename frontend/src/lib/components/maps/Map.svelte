<script>
  import 'leaflet/dist/leaflet.css'
  import { beforeUpdate, createEventDispatcher, onMount, setContext } from 'svelte'
  import { LeafletMap, ScaleControl, TileLayer } from 'svelte-leafletjs'
  import { PUBLIC_INITIAL_VIEW, PUBLIC_INITIAL_ZOOM, PUBLIC_MAX_SW, PUBLIC_MAX_NE } from '$lib/config'
  import { STREET_COLORS, STREET_COLORS_TEXT, DEFAULT_STREET_COLOR } from '$lib/config'
  
  export let map
  export let center = PUBLIC_INITIAL_VIEW
  export let zoom = PUBLIC_INITIAL_ZOOM
  export let minZoom = 5

  let pnoaLayer, scneLayer, osmLayer, layerControl

  const dispatch = createEventDispatcher()
  
  const ortoThreshold = 19
  const mapOptions = { 
    center,
    zoom,
    maxBounds: [PUBLIC_MAX_SW, PUBLIC_MAX_NE],
    minZoom: 5,
    maxZoom: 22,
  }
  const osmAttribution = `&copy; <a href="https://www.openstreetmap.org/copyright"`
  + ` target="_blank">OpenStreetMap</a>`
  const osmUrl = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
  const osmLayerOptions = { minZoom, maxZoom: ortoThreshold, attribution: osmAttribution }
  const scneAttribution = `&copy; <a href="https://www.scne.es"`
  + ` target="_blank">Sistema Cartográfico Nacional</a>`
  const scneUrl = "https://www.ign.es/wms-inspire/ign-base"
  const scneLayerOptions = { minZoom, maxZoom: ortoThreshold, attribution: scneAttribution, layers: 'IGNBaseTodo' }
  const pnoaUrl = "https://www.ign.es/wms-inspire/pnoa-ma"
  const pnoaLayerOptions = { minZoom:ortoThreshold + 1, maxZoom: 22, attribution: scneAttribution, layers: 'OI.OrthoimageCoverage' }
  const scaleControlOptions = { maxWidth: 200, imperial: false }

  let streetNames = []
  
  $: {
    if (map) {
      if (layerControl) layerControl.remove()
      let layers
      if (zoom > ortoThreshold && pnoaLayer) {
        layers = {'PNOA': pnoaLayer()}
      } else if (scneLayer && osmLayer) {
        layers = {'IGN-Base': scneLayer(), 'OSM': osmLayer()}
        map.getMap().attributionControl.removeAttribution(scneAttribution)
      }
      layerControl = L.control.layers(layers).addTo(map.getMap())
    }
  }

  function handleMoveEnd() {
    const latlng = map.getMap().getCenter()
    center = [latlng.lat, latlng.lng]
    zoom = map.getMap().getZoom()
    dispatch('moveend')
  }

  export function getUrl(step = 0) {
    return `${zoom + step}/${center[0].toFixed(4)}/${center[1].toFixed(4)}`
  }

  function addStreetNames(features) {
    for (const feat of features) {
      const tags = feat.properties?.tags || {}
      const name =('highway' in tags) ? tags?.name : (
        tags['addr:street'] || tags['addr:place'] || ''
      )
      if (name && !streetNames.includes(name)) streetNames.push(name)
    }
  }

  function getBgColor(name) {
    const colorIndex = streetNames.indexOf(name) % STREET_COLORS.length
    return colorIndex >= 0 ? STREET_COLORS[colorIndex] : DEFAULT_STREET_COLOR
  }

  function getColor(name) {
    const colorIndex = streetNames.indexOf(name) % STREET_COLORS_TEXT.length
    return colorIndex >= 0 ? STREET_COLORS_TEXT[colorIndex] : 'black'
  }

  setContext('streetNames', {
    add: addStreetNames,
    get: () => streetNames,
    getBgColor,
    getColor,
  })


  beforeUpdate(() => (streetNames = []))

  onMount(() => {
    map.getMap().invalidateSize()
    map.resetZoom = () => {
      map.getMap().setView(PUBLIC_INITIAL_VIEW, PUBLIC_INITIAL_ZOOM)
    }
  })
</script>

<LeafletMap
  bind:this={map}
  options={mapOptions}
  events={['moveend']}
  on:moveend={handleMoveEnd}
>
  {#if zoom > ortoThreshold}
    <TileLayer 
      wms={true}
      url={pnoaUrl}
      options={pnoaLayerOptions}
      bind:getTileLayer={pnoaLayer}
    />
  {:else}
    <TileLayer 
      wms={true}
      url={scneUrl}
      options={scneLayerOptions}
      bind:getTileLayer={scneLayer}
    />
    <TileLayer
      url={osmUrl}
      options={osmLayerOptions}
      bind:getTileLayer={osmLayer}
    />
  {/if}
  <ScaleControl position="bottomleft" options={scaleControlOptions}/>
  <slot></slot>
</LeafletMap>

<style>
  :global(.leaflet-popup-content a img) {
    cursor: zoom-in;
  }
</style>
