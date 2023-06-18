<script>
  import { GeoJSON } from 'svelte-leafletjs'

  export let data


  const fixmeTextStyle = `
    position: absolute;
    top: -35px;
    left: -4px;
    color: white;
    font-size: 1.5rem;
    font-weight: bold;
  `

  const fixmeIconStyle = `
    width: 30px;
    height: 30px;
    border-radius: 50% 50% 50% 0;
    background: red;
    position: absolute;
    transform: rotate(-45deg);
    left: -15px;
    top: -35px;
    border: 2px solid #FFFFFF;
  `

  const fixmeIcon = L.divIcon({
    className: "fixme",
    iconAnchor: [0, 0],
    labelAnchor: [-6, 0],
    popupAnchor: [0, -36],
    tooltipAnchor: [15, -20],
    html: `<span style="${fixmeIconStyle}"></span><span style="${fixmeTextStyle}">!</span>`
  })

  const options = { pointToLayer: createFixme }

  function createFixme(geoJsonPoint, latlng) {
    let marker = L.marker(latlng, { icon: fixmeIcon })
    return marker.bindTooltip(geoJsonPoint.properties?.fixme)
  }
</script>

<GeoJSON {data} {options}/>
