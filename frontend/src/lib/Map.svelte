<script>
  import 'leaflet/dist/leaflet.css'
  import { LeafletMap, ScaleControl, TileLayer } from 'svelte-leafletjs'
	import { createEventDispatcher, onMount } from 'svelte'
  import { PUBLIC_INITIAL_VIEW, PUBLIC_INITIAL_ZOOM } from '$lib/config'
  
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
 
  function handleMoveEnd() {
    const latlng = map.getMap().getCenter()
    center = [latlng.lat, latlng.lng]
    zoom = map.getMap().getZoom()
    dispatch('moveend')
  }

  export function getUrl(step = 0) {
    return `${zoom + step}/${center[0].toFixed(4)}/${center[1].toFixed(4)}`
  }

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
