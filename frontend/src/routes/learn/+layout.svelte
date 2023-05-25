<script>
  import { Sidebar, SidebarWrapper } from 'flowbite-svelte'

  import { getContext } from 'svelte'
  import { afterNavigate } from '$app/navigation'
  
  const drawerHiddenStore = getContext('drawer')

  afterNavigate(() => {
    drawerHiddenStore.set(true)
  })
</script>

<div class="lg:flex">
  <Sidebar
    asideClass="fixed inset-0 z-30 flex-none h-full w-64 lg:static lg:h-auto bg-slate-100 border-r border-gray-300 dark:border-gray-600 lg:overflow-y-visible lg:pt-0 lg:block"
    class="{$drawerHiddenStore && 'hidden'}"
  >
    <SidebarWrapper divClass="overflow-y-auto px-4 pt-20 lg:pt-0 h-full scrolling-touch max-w-2xs lg:h-[calc(100vh-8rem)] lg:block dark:bg-gray-900 lg:mr-0 lg:sticky top-20">
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

  <main class="mx-4 mt-8 lg:mx-auto">
    <slot/>
  </main>
</div>