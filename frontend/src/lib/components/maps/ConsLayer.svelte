<script>
  import { getContext } from 'svelte'
  import { GeoJSON } from 'svelte-leafletjs'

  import { FotoFachadaUrl } from '$lib/config'

  export let data
  export let imageRef
  export let getConsLayer


  const streetNames = getContext('streetNames')


  const options = {
    style,
    pointToLayer: createAddress,
    onEachFeature: function(feature, layer) {
      const tags = JSON.stringify(feature.properties.tags, null, '<br/>')?.replace(/[\"{}]/g, '')
      if (tags) {
        const ref = feature.properties.tags.ref
        layer.bindPopup(`<a href="?ref=${ref}"><img src="${FotoFachadaUrl}${ref}"/></a>` + tags)
        layer.on('popupopen', ({ target }) => imageRef = target.feature.properties?.tags?.ref)
        feature.layer = layer
      }
    },
  }


  function style(feature) {
    if (feature?.properties?.tags?.leisure === 'swimming_pool' ) {
      return { weight: 2, fillOpacity: 0.5, color: '#2299B2' }
    }
    return { weight: 2, fillOpacity: 0.5, color: '#B22222' }
  }


  function getAddress(tags) {
    return tags['addr:street'] || tags['addr:place'] || ''
  }

  function createAddress(geoJsonPoint, latlng) {
    const name = getAddress(geoJsonPoint.properties.tags)
    const housenumber = geoJsonPoint.properties.tags['addr:housenumber']
    let marker = L.marker(latlng, { icon: entranceIcon(name, housenumber) })
    return marker.bindTooltip(name + (housenumber ? ', ' + housenumber : ''))
  }

  function entranceIcon(address, housenumber) {
    const style = `
      background-color: ${streetNames.getBgColor(address)};
      display: ${housenumber ? 'inline' : 'block'};
      min-width: 0.8rem;
      min-height: 0.8rem;
      padding: 0 0.1rem 0 0.1rem;
      left: -0.4rem;
      top: -0.4rem;
      color: ${streetNames.getColor(address)};
      position: relative;
      border: 1px solid ${streetNames.getColor(address)};
    `
    return L.divIcon({
      className: "entrance",
      iconAnchor: [0, 0],
      labelAnchor: [-6, 0],
      popupAnchor: [0, -6],
      html: `<span style="${style}">${housenumber}</span`
    })
  }

  $: streetNames.add(data.features)
</script>

<GeoJSON {data} {options} bind:getGeoJSON={getConsLayer}/>
