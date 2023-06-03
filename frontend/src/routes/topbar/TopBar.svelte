<script>
  import {
    Navbar,
    NavBrand,
    NavLi,
    NavUl,
    NavHamburger,
    ToolbarButton,
  } from 'flowbite-svelte'
  import { Bars3CenterLeft } from 'svelte-heros-v2'
  
  import { getContext } from 'svelte'
  import { invalidate } from '$app/navigation'
  import { page } from '$app/stores'

  import Logo from './Logo.svelte'
  import UserMenu from './UserMenu.svelte'

  export let user

  let ulClass = 'flex flex-col md:flex-row md:space-x-8 items-center order-1 font-medium'

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

  <NavUl {hidden} {ulClass} class="order-1">
    <NavLi href="/learn" active={activeUrl.startsWith('/learn')}>Aprende</NavLi>
    <NavLi href="/explore" active={activeUrl.startsWith('/explore')}>Explora</NavLi>
  </NavUl>

  <div id="usermenu" class="flex md:order-2" on:invalidateuser={invalidateUser}>
    <UserMenu {user}/>
    <NavHamburger on:click={toggle} />
  </div>
</Navbar>
