<script>
  import { FIXME_MSG } from '$lib/config'

  export let fixmes
  export let map
  export let selected

  $: document.getElementById(`fixme_${selected}`)?.scrollIntoView({block: 'center'})

  function centerMap(event, fixme) {
    const point = fixme.geometry.coordinates
    map.getMap().panTo([point[1], point[0]])
    event.preventDefault()
    selected = fixme.properties.id
  }
</script>

<h4>Anotaciones:</h4>
<ol class="mt-0">
  {#each fixmes?.features as fixme}
    <li 
      id={`fixme_${fixme.properties.id}`}
      class={'my-0 ' + (fixme.properties.id === selected ? 'bg-neutral-200 dark:bg-neutral:800' : '')}
    >
      <a
        href="{fixme.properties.id}"
        on:click={(event) => centerMap(event, fixme)}
        data-sveltekit-preload-data="off"
      >
        {FIXME_MSG[fixme.properties.type]}
        {fixme.properties.fixme || ''}
      </a>
    </li>
  {/each}
</ol>
