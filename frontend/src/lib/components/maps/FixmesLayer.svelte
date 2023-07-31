<script>
  import {getContext} from 'svelte';
  import L from 'leaflet'
  import { GeoJSON } from 'svelte-leafletjs'

  import { FIXME_MSG } from '$lib/config'

  export let data
  export let selected = null

  
  const {getMap} = getContext(L)

  const fixmeTextStyle = `
    position: absolute;
    top: -35px;
    left: -4px;
    color: white;
    font-size: 1.5rem;
    font-weight: bold;
  `

  function fixmeIconStyle(selected) {
    return `
      width: 30px;
      height: 30px;
      border-radius: 50% 50% 50% 0;
      background: ${selected ? 'red' : 'darkred'};
      position: absolute;
      transform: rotate(-45deg);
      left: -15px;
      top: -35px;
      border: 2px solid #FFFFFF;
    `
  }

  function fixmeIcon(selected) {
    return L.divIcon({
      className: "fixme",
      iconAnchor: [0, 0],
      labelAnchor: [-6, 0],
      popupAnchor: [0, -36],
      tooltipAnchor: [15, -20],
      html: `<span style="${fixmeIconStyle(selected)}"></span><span style="${fixmeTextStyle}">!</span>`
    })
  }

  $: options = { pointToLayer: (geoJsonPoint, latlng) => createFixme(geoJsonPoint, latlng, selected) }

  function createFixme(geoJsonPoint, latlng, selected) {
    let marker = L.marker(
      latlng,
      {
        icon: fixmeIcon(geoJsonPoint.properties.id === selected),
        riseOnHover: true,
        zIndexOffset: geoJsonPoint.properties.id === selected ? 100 : 0
      }
    )
    const text = `${FIXME_MSG[geoJsonPoint.properties.type]} ${geoJsonPoint.properties?.fixme || ''}`
    return marker.bindTooltip(text)
  }
</script>

<GeoJSON {data} {options}/>
