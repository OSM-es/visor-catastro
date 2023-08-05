<script>
  import { t } from '$lib/translations'
  import FormattedNumber from "$lib/components/FormattedNumber.svelte"

  export let stats
  export let users = true
</script>

<div class="flex space-x-8 mb-16">
  <div class="flex-grow text-center">
    <p class="text-red-500 text-4xl font-extrabold">
      <FormattedNumber value={stats?.buildings}/>
    </p>
    <p>{$t('stats.buildings')}</p>
  </div>
  <div class="flex-grow text-center">
    <p class="text-red-500 text-4xl font-extrabold">
      <FormattedNumber value={stats?.addresses}/>
    </p>
    <p>{$t('stats.addresses')}</p>
  </div>
  {#if users}
    <div class="flex-grow text-center">
      <p class="text-red-500 text-4xl font-extrabold">
        <FormattedNumber value={stats?.users}/>
      </p>
      <p>{$t('stats.users')}</p>
    </div>
  {/if}
  <div class="flex-grow text-center">
    <p class="text-red-500 text-4xl font-extrabold">
      <FormattedNumber value={stats?.mappers}/>
    </p>
    <p>{$t('stats.mappers')}</p>
  </div>
</div>