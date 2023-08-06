<script>
  import { t } from '$lib/translations'
  import FormattedNumber from "$lib/components/FormattedNumber.svelte"

  export let stats
  export let stats2 = null
  export let omit = []
  export let size = 'text-3xl'
  export let ns = 'stats'
  
  let divClass = 'flex flex-wrap mb-16 gap-x-36'
  if (Object.keys(stats).length < 5) divClass += ' justify-between'
</script>

<div class={divClass}>
  {#each Object.entries(stats) as [key, value]}
    {#if !omit.includes(key)}
      <div class="text-center w-24">
        <p class="text-red-500 {size} font-black">
          <FormattedNumber value={value}/>
          {#if stats2}
            / <FormattedNumber value={stats2[key]}/>
          {/if}
        </p>
        <p>{$t(ns + '.' + key)}</p>
      </div>
    {/if}
  {/each}
</div>
