<script>
  import {
    Navbar,
    NavBrand,
    NavLi,
    NavUl,
    NavHamburger,
  } from 'flowbite-svelte'
  
  import { page } from '$app/stores'
  import Logo from './Logo.svelte'
  import UserMenu from './UserMenu.svelte'

  export let user

  let ulClass = 'flex flex-col md:flex-row md:space-x-8 items-center order-1 font-medium'

  $: activeUrl = $page.url.pathname
  $: isMapPage = $page.url.pathname.startsWith('/explore')
</script>

<Navbar
  let:hidden
  let:toggle
  fluid="true"
  navClass="py-0.5 mx-auto {isMapPage ? 'px-2 sm:px-4 w-full': 'max-w-7xl px-4'}"
>
  <NavBrand href="/">
    <Logo/>
  </NavBrand>
  <NavUl {hidden} {ulClass} class="order-1">
    <NavLi href="/learn" active={activeUrl.startsWith('/learn')}>Aprende</NavLi>
    <NavLi href="/explore" active={isMapPage}>Explora</NavLi>
  </NavUl>
  <div class="flex md:order-2">
    <UserMenu {user}/>
    <NavHamburger on:click={toggle} />
  </div>
</Navbar>
