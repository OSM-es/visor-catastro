<script>
  import { setContext } from 'svelte'
  import { writable } from 'svelte/store'
  
  import SideBar from './SideBar.svelte'

  const drawerHiddenStore = writable(true)
  setContext('drawer', drawerHiddenStore)
</script>

<div class="lg:flex">
  <SideBar/>

  <main class="mx-4 mt-8 lg:mx-20">
    <article class="prose md:prose-xl dark:prose-invert">
      <slot/>
    </article>
  </main>
</div>
