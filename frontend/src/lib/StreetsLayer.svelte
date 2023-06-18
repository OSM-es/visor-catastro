<script>
  import { getContext } from 'svelte'
  import { GeoJSON } from 'svelte-leafletjs'

  export let data

  const streetNames = getContext('streetNames')

  const streetOptions = {
    style: streetStyle,
    onEachFeature: function(feature, layer) {
      const name = feature.properties.tags?.name
      if (name) layer.bindTooltip(name, { sticky: true })
    }
  }

  function streetStyle(feature) {
    const name = feature.properties.tags?.name
    const style = { 
      weight: 8,
      opacity: 0.8,
      fillOpacity: 0.3,
      color: streetNames.getBgColor(name)
    }
    return style
  }

  $: streetNames.add(data.features)
</script>

<GeoJSON {data} options={streetOptions}/>
