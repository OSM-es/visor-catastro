<script>
  import {getContext, onDestroy} from 'svelte'
  import L from 'leaflet'
  import { ChevronDown, ChevronUp } from 'svelte-heros-v2'

  const {getMap} = getContext(L)

  export let position = 'bottomleft'
  export let title = 'Leyenda'
  export let collapsed = false

  let legend, div


  $: {
    if (!legend && div) {
      legend = L.control()
      legend.onAdd = function () {
        div.onclick = () => collapsed = !collapsed
        return div
      }
      legend.addTo(getMap())
      legend.setPosition(position)
    }
  }

  onDestroy(() => {
    legend.remove();
  });

  export function getLegend() {
    return legend;
  }
</script>

<div bind:this={div} class="legend">
  <h1>
    {title}
    <span>
      {#if collapsed}<ChevronUp size="14"/>{:else}<ChevronDown size="14"/>{/if}
    </span>
  </h1>
  <div class:hidden={collapsed} class="content">
    <slot/>
  </div>
</div>

<style>
  .legend {
    padding: 6px 8px;
    background: white;
    border: 2px solid rgba(0,0,0,0.2);
    background-clip: padding-box;
    border-radius: 5px;
    color: #111827;
    font-size: medium;
  }
  .legend h1 {
    font-weight: bold;
    display: flex;
    align-items: center;
    text-decoration: underline;
  }
  .legend h1 span {
    margin-left: 0.25rem;
  }
  .legend .content {
    margin-top: 0.4rem;
  }
</style>