<script>
  import '../app.postcss'
  import Topbar from './topbar/TopBar.svelte'

  import { setContext } from 'svelte'
  import { writable } from 'svelte/store'
  
  export let data

  const drawerHiddenStore = writable(true)
  setContext('drawer', drawerHiddenStore)
</script>

<div class="min-h-screen flex flex-col dark:bg-neutral-900">
  <header
    class="sticky top-0 z-40 w-full drop-shadow-md"
  >
  <Topbar user={data.user}/>
  </header>

  <slot/>
</div>
