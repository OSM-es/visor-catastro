<script>
  import { Select } from 'flowbite-svelte'

  import { t, locale, locales } from '$lib/translations'
</script>

<Select size="sm" bind:value="{$locale}" placeholder={false}>
  {#each $locales as value}
    <option value="{value}">{$t(`lang.${value}`)}</option>
  {/each}
</Select>
