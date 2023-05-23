<script>
  import 'leaflet/dist/leaflet.css'
  import { GeoJSON, LeafletMap, ScaleControl, TileLayer } from 'svelte-leafletjs'
	import { createEventDispatcher, onMount } from 'svelte'
  import { PUBLIC_INITIAL_VIEW, PUBLIC_INITIAL_ZOOM } from '$lib/config'

  export let map
  export let geoJsonData
  export let geoJsonOptions = {}
  export let center = PUBLIC_INITIAL_VIEW
  export let zoom = PUBLIC_INITIAL_ZOOM

  let getGeoJSON

  const dispatch = createEventDispatcher()

  const attribution = `&copy; <a href="https://www.openstreetmap.org/copyright"`
    + `target="_blank">OpenStreetMap</a>`
  const mapOptions = { center, zoom }
  const tileUrl = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
  const tileLayerOptions = { minZoom: 5, maxZoom: 19, attribution }
  const scaleControlOptions = { maxWidth: 200, imperial: false }

  onMount(() => {
    if (geoJsonData) {
      map.getMap().invalidateSize()
      const bounds = getGeoJSON().getBounds()
      map.getMap().fitBounds(bounds)
    }
  })
</script>

<LeafletMap
  bind:this={map}
  options={mapOptions}
  events={['moveend']}
  on:moveend={() => dispatch('moveend')}
>
  <TileLayer url={tileUrl} options={tileLayerOptions}/>
  <ScaleControl position="bottomleft" options={scaleControlOptions}/>
  <GeoJSON data={geoJsonData} options={geoJsonOptions} bind:getGeoJSON/>
</LeafletMap>
