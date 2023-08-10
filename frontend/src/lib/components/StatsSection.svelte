<script>
  import { t } from '$lib/translations'
  import FormattedNumber from "$lib/components/FormattedNumber.svelte"

  export let stats
  export let stats2 = null
  export let omit = []
  export let size = 'text-3xl'
  export let ns = 'stats'
  export let gap = 'gap-x-12'
  
  let divClass = `flex flex-wrap ${gap} gap-y-8`
  if (Object.keys(stats).length < 5) divClass += ' justify-between'
</script>

<div class={divClass}>
  {#each Object.entries(stats) as [key, value]}
    {#if !omit.includes(key)}
      <div class="text-center w-24">
        <p class="text-red-500 {size} font-black">
          {#if typeof(value) === 'number'}
            <FormattedNumber value={value}/>
          {:else}
            {value}
          {/if}
          {#if stats2}
            / {#if typeof(value) === 'number'}
              <FormattedNumber value={stats2[key]}/>
              {:else}
              {value}
            {/if}
          {/if}
        </p>
        <p>{$t(ns + '.' + key, { value })}</p>
      </div>
    {/if}
  {/each}
</div>
