<script>
  import { invalidate } from '$app/navigation'
  import { locale } from '$lib/translations'
  import { browser } from '$app/environment'

  export let data

  locale.subscribe((value) => {
    if (browser) invalidate('data:locale')
  })
</script>

<svelte:component this={data.content} user={data.user}/>

