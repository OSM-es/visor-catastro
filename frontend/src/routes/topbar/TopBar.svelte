<script>
  import {
    Navbar,
    NavBrand,
    NavLi,
    NavUl,
    NavHamburger,
    ToolbarButton,
  } from 'flowbite-svelte'
  import { BookOpen, Bars3CenterLeft, Map } from 'svelte-heros-v2'
  
  import { getContext } from 'svelte'
  import { invalidate } from '$app/navigation'
  import { page } from '$app/stores'

  import Logo from './Logo.svelte'
  import UserMenu from './UserMenu.svelte'

  export let user

  const ulClass = 'flex flex-col md:flex-row md:space-x-8 items-center bg-transparent dark:bg-transparent border-0 sm:max-md:text-sm font-medium'
  const activeClass = 'bg-transparent text-primary-700 dark:text-white md:dark:bg-transparent'
  const nonActiveClass = 'text-gray-700 hover:text-primary-500 dark:text-gray-400 dark:hover:text-gray-300'
  const _liClass = 'flex items-center !py-0'

  $: activeUrl = $page.url.pathname

  const drawerHiddenStore = getContext('drawer')

  function toggleDrawer() {
    drawerHiddenStore.update((state) => !state)
  }

  async function invalidateUser() {
    await invalidate('data:user')
  }
</script>

<Navbar
  let:hidden
  let:toggle
  fluid="true"
  navClass="py-0.5 mx-auto px-4 w-full dark:!bg-[#2E2E2E]"
>
  <div class="flex items-center">
    <span hidden={!activeUrl.startsWith('/learn')}>
      <ToolbarButton
        name="Abre tabla de contenido"
        class="px-1.5 lg:hidden"
        on:click={toggleDrawer}
      >
        <Bars3CenterLeft/>
      </ToolbarButton>
    </span>
    <NavBrand href="/">
      <Logo/>
    </NavBrand>
  </div>

  <NavUl {hidden} {ulClass} {activeClass} {nonActiveClass} class="order-1">
    <NavLi href="/learn" active={activeUrl.startsWith('/learn')} class={_liClass}>
      <BookOpen class="w-5 m-1"/> Aprende
    </NavLi>
    <NavLi href="/explore" active={activeUrl.startsWith('/explore')} class={_liClass}>
      <Map class="w-5 m-1"/> Explora
    </NavLi>
  </NavUl>

  <div id="usermenu" class="flex md:order-2" on:invalidateuser={invalidateUser}>
    <UserMenu {user}/>
    <NavHamburger on:click={toggle} />
  </div>
</Navbar>
