<script>
  import { GeoJSON } from 'svelte-leafletjs'

  export let data


  const style = (feature) => ({ weight: 1, fillOpacity: 0.3, color: '#B22222' })
  const options = { style }
</script>

<GeoJSON {data} {options}/>
