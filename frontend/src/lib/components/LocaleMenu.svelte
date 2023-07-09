<script>
  import { Select } from 'flowbite-svelte'

  import { t, locale, locales } from '$lib/translations'
</script>

<Select name="locale" bind:value="{$locale}" size="sm" placeholder={false}>
  {#each $locales as value}
    <option value="{value}">{$t(`lang.${value}`)}</option>
  {/each}
</Select>
