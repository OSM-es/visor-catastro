<script>
  import { Progressbar, Spinner } from 'flowbite-svelte'
  import { afterNavigate, goto } from '$app/navigation'
  import { GeoJSON } from 'svelte-leafletjs'
  import { locale } from '$lib/translations'
  import { page } from '$app/stores'
  import 'leaflet.pattern'

  import TaskList from './TaskList.svelte'
  import TaskStatus from './TaskStatus.svelte'
  import ProjList from './ProjList.svelte'
  import { exploreCode } from '$lib/stores.js'

  import { AREA_BORDER, TASK_COLORS, TASK_LOCKED_COLOR, TASK_DIFFICULTY_VALUES, TASK_STATUS_VALUES, TASK_TYPE_VALUES, TASK_THR, MUN_THR } from '$lib/config'
  import Map from '$lib/components/maps/Map.svelte'
  import Legend from '$lib/components/maps/Legend.svelte'

  export let data

  let map, geoJsonData, activeItem, getUrl, getGeoJSON
  let muncode, type, difficulty, ad_status, bu_status
  let loading = false
  let delayed = false
  let center = data.center
  let zoom = data.zoom
  let project
  let timer
  let pattern

  $: code = $page?.params?.code

  const geojsonUrl = (target, code, bounds) => {
    return `${data.api}/${target}?${code ? 'code=' + code : ''}&bounds=${bounds}`
  }
  const rightBarClass = 'md:max-w-md w-full flex-grow overflow-scroll px-4 '
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
    if (
      from?.route?.id === '/explore/[[code]]'
      && to?.route?.id === '/explore/[[code]]'
    ) {
      exploreCode.set(code)
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
    if (activeItem && !layer) {
      activeItem = null
    } else if (!activeItem && layer) {
      activeItem = feature
    }
    layer?.bringToFront()
  }

  function setStyle(feature, activeItem) {
    let style

    if (!pattern) {
      const shape = new L.PatternPath({
        x: 6,
        y: 6,
        color: 'red',
        d: "M9.182 9.182C10.93935 7.4246 10.93935 4.57538 9.182 2.81802C7.4246 1.06066 4.57538 1.06066 2.81802 2.81802M9.182 9.182C7.4246 10.93935 4.57538 10.93935 2.81802 9.182C1.06066 7.4246 1.06066 4.57538 2.81802 2.81802M9.182 9.182L2.81802 2.81802",
        fill: false,
        opacity: 1,
      })
      pattern = new L.Pattern({width:18, height:18, color: 'red'})
      pattern.addShape(shape)
      pattern.addTo(map.getMap())
    }

    if (target(zoom) === 'tasks') {
      const options = {
        color: feature.properties.lock_id ? TASK_LOCKED_COLOR : TASK_COLORS[feature.properties.bu_status],
        spaceColor: feature.properties.lock_id ? TASK_LOCKED_COLOR : TASK_COLORS[feature.properties.ad_status],
        opacity: 1,
        spaceOpacity: 1,
        angle: -45,
      }
      const stripes = new L.StripePattern(options)
      stripes.addTo(map.getMap())
      style = {
        fillPattern: feature.properties.lock_id ? pattern : stripes,
        fillOpacity: 1,
      }
    } else {
      style = { 
        fillPattern: feature?.properties?.update_id ? pattern : null,
        fillColor: 'blue',
        fillOpacity: feature?.properties?.update_id ? 0.6 : 0.2,
      }
    }
    if (feature.properties.id === activeItem?.properties?.id) {
      style.weight = 2
      style.color = 'black'
    } else {
      style.weight = 1
      style.color = AREA_BORDER 
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

  $: geoJsonOptions = {
    style: (feature) => setStyle(feature, activeItem),
    onEachFeature: function(feature, layer) {
      layer.bindTooltip(featInfo(feature.properties))
      layer.on('click', (event) => handleClick(event, feature))
      layer.on('dblclick', () => clearTimeout(timer))
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
      {#if zoom >= TASK_THR}
        <Legend>
          <TaskStatus status="READY"/>
          <TaskStatus status="MAPPED"/>
          <TaskStatus status="INVALIDATED"/>
          <TaskStatus status="VALIDATED"/>
          <TaskStatus status="NEED_UPDATE"/>
          <TaskStatus status="MIXED"/>
          <TaskStatus status="LOCKED"/>
        </Legend>
      {/if}
    </Map>
  </div>
  <div class={rightBarClass}>
    <div class="h-full max-h-0">
      {#if loading && delayed}
        <p class="mt-4">Cargando datos... 
          <Spinner size={4} />
        </p>
      {:else if target(zoom) === 'tasks'}
        {#if geoJsonData?.features?.length > 0}
          <TaskList
            tasks={tasks.features}
            bind:muncode
            bind:type
            bind:difficulty
            bind:ad_status
            bind:bu_status
            bind:activeItem
            on:click={(event) => handleClick(event.detail.feature)}
            on:mouseover={(event) => handleMouseover(event.detail.feature)}
            on:mouseout={() => handleMouseover()}
          />
        {:else}
          <p class="w-full bg-neutral-100 dark:bg-neutral-700 p-2 mt-3">
            No hay tareas aquí
          </p>
        {/if}
      {:else}
        {#if code}
        <div class="prose dark:prose-invert pt-3">
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
            bind:activeItem
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
