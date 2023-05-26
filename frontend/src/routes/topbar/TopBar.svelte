<script>
  import {
    Navbar,
    NavBrand,
    NavLi,
    NavUl,
    NavHamburger,
    ToolbarButton,
  } from 'flowbite-svelte'
  
  import { page } from '$app/stores'
  import { getContext } from 'svelte'

  import Logo from './Logo.svelte'
  import UserMenu from './UserMenu.svelte'

  export let user

  let ulClass = 'flex flex-col md:flex-row md:space-x-8 items-center order-1 font-medium'

  $: activeUrl = $page.url.pathname

  const drawerHiddenStore = getContext('drawer')

  const toggleDrawer = () => {
    drawerHiddenStore.update((state) => !state)
  }
</script>

<Navbar
  let:hidden
  let:toggle
  fluid="true"
  navClass="py-0.5 mx-auto px-4 w-full"
>
  <div class="flex items-center">
    <span hidden={!activeUrl.startsWith('/learn')}>
      <ToolbarButton
        name="Abre tabla de contenido"
        class="px-2.5 lg:hidden"
        on:click={toggleDrawer}
      >
        <div class="w-4 h-0.5 bg-gray-500 mb-1 mt-1.5"></div>
        <div class="w-3 h-0.5 bg-gray-500 mb-1"></div>
        <div class="w-4 h-0.5 bg-gray-500 mb-1.5"></div>
      </ToolbarButton>
    </span>
    <NavBrand href="/">
      <Logo/>
    </NavBrand>
  </div>

  <NavUl {hidden} {ulClass} class="order-1">
    <NavLi href="/learn" active={activeUrl.startsWith('/learn')}>Aprende</NavLi>
    <NavLi href="/explore" active={activeUrl.startsWith('/explore')}>Explora</NavLi>
  </NavUl>

  <div class="flex md:order-2">
    <UserMenu {user}/>
    <NavHamburger on:click={toggle} />
  </div>
</Navbar>

<style>
  .bar {
    width: 18px;
    height: 2px;
    background-color: gray;
    margin: 3px 0;
  }
</style>