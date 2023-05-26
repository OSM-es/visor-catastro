<script>
  import { Sidebar, SidebarWrapper } from 'flowbite-svelte'

  import { getContext } from 'svelte'
  import { afterNavigate } from '$app/navigation'
  
  const drawerHiddenStore = getContext('drawer')

  function closeDrawer() {
    drawerHiddenStore.set(true)
  }

  afterNavigate(closeDrawer)
</script>

<div class="lg:flex">
  <Sidebar
    asideClass="fixed inset-0 z-30 flex-none h-full w-1/4 lg:static lg:h-auto bg-slate-100 border-r border-gray-300 dark:border-gray-600 lg:overflow-y-visible lg:block"
    class="{$drawerHiddenStore && 'hidden'}"
  >
    <SidebarWrapper divClass="overflow-y-auto w-64 min-w-1/6 ml-auto px-4 pt-16 lg:pt-6 h-full scrolling-touch lg:h-[calc(100vh-4rem)] lg:block lg:mr-0 lg:sticky top-14">
      <ul>
        <li>blablablabla</li>
        <li>blablabla</li>
        <li>blabla</li>
        <li>blablablabla</li>
        <li>blablablabla</li>
        <li>blablablabla</li>
      </ul>
    </SidebarWrapper>
  </Sidebar>

  <div
    hidden={$drawerHiddenStore}
    class="fixed inset-0 z-20 bg-gray-900/50 dark:bg-gray-200/50"
    on:click={closeDrawer}
    on:keydown={closeDrawer}
  />

  <main class="mx-4 mt-8 lg:mx-auto">
    <slot/>
  </main>
</div>