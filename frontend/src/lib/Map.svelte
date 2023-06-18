<script>
  import 'leaflet/dist/leaflet.css'
	import { beforeUpdate, createEventDispatcher, onMount, setContext } from 'svelte'
  import { LeafletMap, ScaleControl, TileLayer } from 'svelte-leafletjs'
  import { PUBLIC_INITIAL_VIEW, PUBLIC_INITIAL_ZOOM } from '$lib/config'
  import { STREET_COLORS, STREET_COLORS_TEXT, DEFAULT_STREET_COLOR } from '$lib/config'
  
  export let map
  export let center = PUBLIC_INITIAL_VIEW
  export let zoom = PUBLIC_INITIAL_ZOOM
  export let minZoom = 5

  const dispatch = createEventDispatcher()
  
  const attribution = `&copy; <a href="https://www.openstreetmap.org/copyright"`
  + `target="_blank">OpenStreetMap</a>`
  const mapOptions = { center, zoom }
  const tileUrl = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
  const tileLayerOptions = { minZoom, maxZoom: 19, attribution }
  const scaleControlOptions = { maxWidth: 200, imperial: false }

  let streetNames = []
 
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
  })
</script>

<LeafletMap
  bind:this={map}
  options={mapOptions}
  events={['moveend']}
  on:moveend={handleMoveEnd}
>
  <TileLayer url={tileUrl} options={tileLayerOptions}/>
  <ScaleControl position="bottomleft" options={scaleControlOptions}/>
  <slot></slot>
</LeafletMap>

<style>
  :global(.leaflet-popup-content a img) {
    cursor: zoom-in;
  }
</style>