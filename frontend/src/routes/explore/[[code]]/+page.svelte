<script>
  import { Progressbar, Spinner } from 'flowbite-svelte'
  import { afterNavigate, goto } from '$app/navigation'
  import { GeoJSON } from 'svelte-leafletjs'
  import { locale } from '$lib/translations'
  import { page } from '$app/stores'

  import TaskList from './TaskList.svelte'
  import ProjList from './ProjList.svelte'

  import { TASK_COLORS, TASK_LOCKED_COLOR, TASK_DIFFICULTY_VALUES, TASK_STATUS_VALUES, TASK_TYPE_VALUES, TASK_THR, MUN_THR } from '$lib/config'
  import Map from '$lib/components/maps/Map.svelte'

  export let data

  
  let map, geoJsonData, hoveredFeature, previewFeature, getUrl, getGeoJSON
  let muncode, type, difficulty, ad_status, bu_status
  let loading = false
  let delayed = false
  let center = data.center
  let zoom = data.zoom
  let project
  let timer

  $: code = $page?.params?.code

  const geojsonUrl = (target, code, bounds) => {
    return `${data.api}/${target}?${code ? 'code=' + code : ''}&bounds=${bounds}`
  }
  const rightBarClass = 'md:max-w-md w-full flex-grow overflow-scroll px-4 pt-3 '
    + 'border-l-2 border-neutral-300 dark:border-neutral-500 dark:bg-neutral-800'

  const target = (zoom) => (
    zoom >= TASK_THR ? 
    'tasks' : 
    (zoom >= MUN_THR ? 'municipalities' : 'provinces')
  )
  const fmt = new Intl.NumberFormat($locale, { maximumFractionDigits: 2, style: "percent" })

  $: tasks = filterTasks(geoJsonData, muncode, type, difficulty, ad_status, bu_status)

  function setZoom(zoom) {
    map.getMap().fitBounds(getGeoJSON().getBounds())
    map.getMap().setZoom(zoom)
  }


  afterNavigate(async ({from, to}) => {
    if (to?.route?.id === '/explore/[[code]]') {
      await fetchData()
      if (code && code !== from?.params?.code) {
        project = geoJsonData.features[0].properties
        map.getMap().fitBounds(getGeoJSON().getBounds())
      }
    }
  })

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
    const code = $page.params?.code
    const bounds = map.getMap().getBounds().toBBoxString()
    const response = await fetch(geojsonUrl(target(zoom), code, bounds))
    geoJsonData = await response.json()
    loading = false
  }

  function handleMoveEnd() {
    goto(`${$page.url.pathname}?map=${getUrl()}`, { replaceState: true })
  }

  function updateStyle(feature, layer) {
    if (layer) {
      layer.setStyle(setStyle(feature))
    } else {
      geoJsonData = geoJsonData
    }
  }

	function handleClick(event, feature) {
    const t = target(zoom)
    if (event.originalEvent.detail === 1) {
      timer = setTimeout(() => {
        if (t === 'tasks') {
          goto('/explore/task/' + feature.properties.id)
        } else if (t === 'municipalities') {
          goto('/explore/' + feature.properties.muncode)
        } else if (t === 'provinces') {
          goto('/explore/' + feature.properties.provcode)
        }
      }, 200)
    }
	}

  function handleMouseover(feature, layer) {
    hoveredFeature = feature
    previewFeature = layer ? feature : null
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
    } else {
      style = { 
        fillColor: 'blue',
        fillOpacity: 0.2,
        weight: 2,
      }
    }
    if (feature.properties.id === hoveredFeature?.properties?.id) {
      style.dashArray = '5,5'
      style.weight = 2
      style.color = 'black'
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
      layer.on('click', (event) => handleClick(event, feature))
      layer.on('dblclick', (event) => (clearTimeout(timer)))
      layer.on('mouseover', () => handleMouseover(feature, layer))
      layer.on('mouseout', () => handleMouseover(null, null))
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
      <GeoJSON data={tasks} options={geoJsonOptions} bind:getGeoJSON/>
    </Map>
  </div>
  <div class={rightBarClass}>
    <div class="h-full max-h-0">
      {#if loading && delayed}
        <p class="mt-4">Cargando datos... 
          <Spinner size={4} />
        </p>
      {:else if target(zoom) === 'tasks'}
        <TaskList
          tasks={tasks.features}
          bind:muncode
          bind:type
          bind:difficulty
          bind:ad_status
          bind:bu_status
          activeItem={hoveredFeature?.id}
          on:click={(event) => handleClick(event.detail.feature)}
          on:mouseover={(event) => handleMouseover(event.detail.feature)}
          on:mouseout={() => handleMouseover()}
        />
      {:else}
        {#if code}
        <div class="prose dark:prose-invert pb-2">
          <h3>{project?.name} ({code})</h3>
        </div>
        {/if}
        {#if code?.length === 5}
          <div class="space-y-6 pt-4">
            <div class="!space-y-1">
              <p class="flex justify-between">
                <span>Tareas:</span>
                <span>{project?.task_count}</span>
              </p>
              {#if project?.task_count}
                <p class="flex justify-between">
                  <span>Mapeado:</span>
                  <span>{fmt.format(project.mapped_count / project?.task_count)}</span>
                </p>
                  <Progressbar
                  progress = {100 * project.mapped_count / project.task_count}
                  size="h-4"
                  color="gray"
                />
              {/if}
            </div>
            <p>
              Haz <button class="text-primary-600" on:click={() => setZoom(TASK_THR)}>zoom</button>
              para ver las tareas o
              <a class="text-primary-600" href="/explore">explora</a>
              el resto de municipios.
            </p>
          </div>
        {:else}
          <ProjList
            data={geoJsonData?.features}
            target={target(zoom)}
            activeItem={hoveredFeature?.id}
            {map}
            on:mouseover={(event) => handleMouseover(event.detail.feature)}
            on:mouseout={() => handleMouseover()}
          />
          {#if code?.length == 2}
            <p class="pt-4">
              <a class="text-primary-600" href="/explore">Explora</a>
              el resto de provincias.
            </p>
        {/if}
        {/if}
      {/if}
    </div>
  </div>
</div>
