<script>
  import '../app.postcss'
  import Topbar from './topbar/TopBar.svelte'

  import { setContext } from 'svelte'
  import { writable } from 'svelte/store'
  
  export let data

  const drawerHiddenStore = writable(true)
  setContext('drawer', drawerHiddenStore)
</script>

<div class="h-screen flex flex-col dark:bg-gray-900">
  <header
    class="sticky top-0 z-40 w-full border-b border-gray-200 dark:border-gray-600"
  >
  <Topbar user={data.user}/>
  </header>

  <slot/>
</div>
