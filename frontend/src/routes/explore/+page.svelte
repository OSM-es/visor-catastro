<script>
  import { Spinner } from 'flowbite-svelte'
  import TaskList from './TaskList.svelte'
  import { goto } from '$app/navigation'
  import { GeoJSON } from 'svelte-leafletjs'
  import { locale } from '$lib/translations'

  import { TASK_COLORS, TASK_LOCKED_COLOR, TASK_DIFFICULTY_VALUES, TASK_STATUS_VALUES, TASK_TYPE_VALUES } from '$lib/config'
  import Map from '$lib/components/maps/Map.svelte'

  export let data


  let map, geoJsonData, hoveredFeature, previewFeature, getUrl
  let muncode, type, difficulty, ad_status, bu_status
  let loading = false
  let delayed = false
  let center = data.center
  let zoom = data.zoom

  const tasksThreshold = 15
  const munThreshold = 8
  const geojsonUrl = (target, bounds) => `${data.api}/${target}?bounds=${bounds}`
  const rightBarClass = 'md:max-w-md w-full flex-grow overflow-scroll px-4 pt-3 '
    + 'border-l-2 border-neutral-300 dark:border-neutral-500 dark:bg-neutral-800'

  const target = (zoom) => (
    zoom >= tasksThreshold ? 
    'tasks' : 
    (zoom >= munThreshold ? 'municipalities' : 'provinces')
  )

  $: tasks = filterTasks(geoJsonData, muncode, type, difficulty, ad_status, bu_status)


  function filterTasks(geoJsonData, muncode, type, difficulty, ad_status, bu_status) {
    let data = geoJsonData?.features || []
    if (data) {
      if (muncode) data = data.filter(t => t.properties.muncode === muncode)
      if (type) data = data.filter(t => t.properties.type === type)
      if (difficulty) data = data.filter(t => t.properties.difficulty === difficulty)
      if (ad_status) data = data.filter(t => t.properties.ad_status === ad_status)
      if (bu_status) data = data.filter(t => t.properties.bu_status === bu_status)
    }
    return { type: 'FeatureCollection', features: data }
  }

  async function fetchData() {
    loading = true
    delayed = false
    setTimeout(() => (delayed = true), 500)
    const bounds = map.getMap().getBounds().toBBoxString()
    const response = await fetch(geojsonUrl(target(zoom), bounds))
    geoJsonData = await response.json()
    loading = false
  }

  function handleMoveEnd() {
    fetchData()
    goto(`/explore?map=${getUrl()}`, { replaceState: true })
  }

  function updateStyle(feature, layer) {
    if (layer) {
      layer.setStyle(setStyle(feature))
    } else {
      geoJsonData = geoJsonData
    }
  }

	function handleClick(feature) {
    if (target(zoom) === 'tasks') {
      goto('/explore/task/' + feature.properties.id)
    }
	}

  function handleMouseover(feature, layer) {
    hoveredFeature = feature
    previewFeature = layer ? feature : null
    updateStyle(feature, layer)
  }

  function handleMouseout(feature, layer) {
    hoveredFeature = null
    previewFeature = null
    updateStyle(feature, layer)
  }

  function setStyle(feature) {
    let style
    if (target(zoom) === 'tasks') {
      style = { 
        fillColor: feature.properties.lock_id ? TASK_LOCKED_COLOR : TASK_COLORS[feature.properties.status],
        fillOpacity: feature.properties.bu_status == feature.properties.ad_status ? 1 : 0.5,
        dashArray: null,
        weight: 1,
        color: '#3388ff', 
      }
      if (feature.properties.id === hoveredFeature?.properties?.id) {
        style.dashArray = '5,5'
        style.weight = 2
        style.color = 'black'
      }
    } else {
      style = { 
        fillColor: 'blue',
        fillOpacity: 0.2,
        weight: 2,
      }
    }
    return style
  }

  function getStatus(feat) {
    if (feat.lock_id) {
      return 'Bloqueada'
    } else if (feat.bu_status === feat.ad_status) {
      return TASK_STATUS_VALUES[feat.bu_status]
    } else {
      return `${TASK_STATUS_VALUES[feat.bu_status]} (edificios), ${TASK_STATUS_VALUES[feat.ad_status]} (direcciones)`
    }
  }

  function featInfo(feat) {
    let info = ''
    if (feat.provcode) {
      info = `<ul><li>Provincia: ${feat.name} (${feat.provcode})</li>`
    } else {
      info = `<ul><li>Municipio: ${feat.name} (${feat.muncode})</li>`
    }
    if (feat.localid) {
      info += `
        <li>Tipo: ${TASK_TYPE_VALUES[feat.type]}</li>
        <li>Dificultad: ${TASK_DIFFICULTY_VALUES[feat.difficulty]}</li>
        <li>Estado: ${getStatus(feat)}</li>
      `
    } else {
      const mapped = feat.mapped_count / feat.task_count
      const fmt = new Intl.NumberFormat($locale, { maximumFractionDigits: 2, style: "percent" })
      info += `
        <li>Tareas: ${feat.task_count}</li>
        <li>Mapeado: ${fmt.format(mapped)}</li>
      `
    }
    info += '</ul>'
    return info
  }

  const geoJsonOptions = {
    style: setStyle,
    onEachFeature: function(feature, layer) {
      layer.bindTooltip(featInfo(feature.properties))
      layer.on('click', () => handleClick(feature, layer))
      layer.on('mouseover', () => handleMouseover(feature, layer))
      layer.on('mouseout', () => handleMouseout(feature, layer))
    },
  }
</script>

<div class="flex flex-col md:flex-row flex-grow">
  <div class="w-full flex-grow z-0">
    <Map
      bind:map
      bind:center
      bind:zoom
      bind:getUrl
      on:moveend={handleMoveEnd}
    >
      <GeoJSON data={tasks} options={geoJsonOptions}/>
    </Map>
  </div>
  <div class={rightBarClass}>
    <div class="h-full max-h-0">
      {#if loading && delayed}
        <p class="mt-4">Cargando datos... 
          <Spinner size={4} />
        </p>
      {:else if target(zoom) === 'provinces'}
        <div class="prose lg:prose-xl dark:prose-invert">
          <p>
            Aquí se visalizará estadísticas de la importación por provincias.
          </p>
          <p>Haz zoom al nivel de escala 50 km o en una provincia para ver los municipios.</p>
        </div>
      {:else if target(zoom) === 'municipalities'}
        <div class="prose lg:prose-xl dark:prose-invert">
          <p>
            Aquí se visalizará estadísticas de la importación por municipios.
          </p>
          <p>Haz zoom al nivel de escala 500 m o en un municipio para ver las tareas.</p>
        </div>
      {:else}
        <TaskList
          tasks={tasks.features}
          bind:muncode
          bind:type
          bind:difficulty
          bind:ad_status
          bind:bu_status
          on:click={(event) => handleClick(event.detail.feature)}
          on:mouseover={(event) => handleMouseover(event.detail.feature)}
          on:mouseout={() => handleMouseover()}
        />
      {/if}
    </div>
  </div>
</div>
