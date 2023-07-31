<script>
  import { Checkbox } from 'flowbite-svelte'

  import { FIXME_MSG } from '$lib/config'

  export let fixmes
  export let map
  export let selected
  export let lock

  $: scrollIntoViewIfVisible(document.getElementById(`fixme_${selected}`))

  function centerMap(event, fixme) {
    const point = fixme.geometry.coordinates
    map.getMap().panTo([point[1], point[0]])
    selected = fixme.properties.id
  }

  function scrollIntoViewIfVisible(target) {
    if (target) {
      if (target.getBoundingClientRect().bottom > window.innerHeight) {
        target.scrollIntoView({block: 'center'})
      } else if (target.getBoundingClientRect().top < 150) {
        target.scrollIntoView({block: 'center'})
      }
    }
  }
</script>

<h4>Anotaciones:</h4>
<ol class="mt-0">
  {#each fixmes?.features as fixme}
    <!-- svelte-ignore a11y-click-events-have-key-events -->
    <li 
      id={`fixme_${fixme.properties.id}`}
      class={'my-0 cursor-pointer ' + (fixme.properties.id === selected ? 'bg-neutral-200 dark:bg-neutral:800' : '')}
      on:click={(event) => centerMap(event, fixme)}
    >
      <form class="inline mr-1">
        <Checkbox disabled={!lock}/>
      </form>
      {FIXME_MSG[fixme.properties.type]}
      {fixme.properties.fixme || ''}
    </li>
  {/each}
</ol>
