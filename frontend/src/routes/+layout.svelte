<script>
  import { page } from '$app/stores'
  
  import '../app.postcss'
  import Topbar from './topbar/TopBar.svelte'
  
  export let data

  $: headerClass = $page.url.pathname.startsWith('/explore') ? 'h-screen' : 'min-h-screen'
</script>

<div class="{headerClass} flex flex-col dark:bg-neutral-900 dark:text-neutral-100">
  <header
    class="sticky top-0 z-40 w-full drop-shadow-md"
  >
    <Topbar user={data.user}/>
  </header>

  <slot/>
</div>
