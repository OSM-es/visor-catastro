<script>
  import { CloseButton, Sidebar, SidebarWrapper } from 'flowbite-svelte'

  import { getContext } from 'svelte'
  import { afterNavigate } from '$app/navigation'
  import { page } from '$app/stores'

  import Toc from '../toc.svx'

  const drawerHiddenStore = getContext('drawer')
  const asideClass = 'fixed inset-0 z-30 flex-none h-full w-1/4 lg:static '
    + 'text-gray-700 dark:text-gray-300 bg-neutral-100 dark:bg-neutral-800 border-r '
    + 'border-neutral-300 dark:border-neutral-500 '
    + 'lg:h-auto lg:overflow-y-visible lg:block'
  const divClass = 'overflow-y-auto bg-inherit w-64 ml-auto pl-4 pr-1 '
    + 'pt-16 lg:pt-6 h-full scrolling-touch lg:h-[calc(100vh-4rem)] '
    + 'lg:block lg:mr-0 lg:sticky top-14'

  function setActiveLink(node) {
    return {
      destroy: page.subscribe(page => {
        const url = page.url.pathname
        node.querySelectorAll('a').forEach(a => { 
          if (a.getAttribute('href') === url) {
            a.classList.add('active') 
          } else {
           a.classList.remove('active')
          }
        })
      })
    }
  }

  function closeDrawer() {
    drawerHiddenStore.set(true)
  }

  afterNavigate(closeDrawer)
</script>

<Sidebar {asideClass} class="{$drawerHiddenStore && 'hidden'}">
  <SidebarWrapper {divClass}>
    <nav use:setActiveLink>
      <Toc/>
    </nav>
  </SidebarWrapper>
</Sidebar>

<div
  hidden={$drawerHiddenStore}
  class="fixed inset-0 z-20 bg-gray-900/50 dark:bg-gray-200/50 text-right pt-16 pr-3"
  on:click={closeDrawer}
  on:keydown={closeDrawer}
>
  <CloseButton name="Cierra tabla de contenido" class="dark:text-white"/>

  <style>
    nav {
      line-height: 1.6;
    }

    a:hover, a.active {
      text-decoration: underline;
    }
  
    a.active::after {
      float:right;
      content: url('data:image/svg+xml;utf8,<svg fill="gray" width="24" height="24" xmlns="http://www.w3.org/2000/svg"><g><path d="M4,11V13H16L10.5,18.5L11.92,19.92L19.84,12L11.92,4.08L10.5,5.5L16,11H4Z" /></g></svg>');
    }
  </style>  
</div>
