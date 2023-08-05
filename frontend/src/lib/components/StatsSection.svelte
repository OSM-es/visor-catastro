<script>
  import { t } from '$lib/translations'
  import FormattedNumber from "$lib/components/FormattedNumber.svelte"

  export let stats
  export let omit = []
  export let size = 'text-3xl'
</script>

<div class="flex space-x-8 mb-16">
  {#each Object.entries(stats) as [key, value]}
    {#if !omit.includes(key)}
      <div class="flex-grow text-center">
        <p class="text-red-500 {size} font-black">
          <FormattedNumber value={value}/>
        </p>
        <p>{$t('stats.' + key)}</p>
      </div>
    {/if}
  {/each}
</div>
