<script>
  import '../app.postcss';
  import { page } from '$app/stores';
  import {
    Avatar,
    Button,
    Chevron,
    DarkMode,
    Dropdown,
    DropdownItem,
    Navbar,
    NavBrand,
    NavLi,
    NavUl,
    NavHamburger,
  } from 'flowbite-svelte'
  import logo from '$lib/images/Logo-spain-geo.png'
  let avatar = 'https://upload.wikimedia.org/wikipedia/commons/8/8b/Creative-Tail-People-man-2.svg'
  let signup = 'https://www.openstreetmap.org/user/new'
  let ulClass = 'flex flex-col md:flex-row md:space-x-8 items-center order-1 font-medium'
  let logged = false
  $: activeUrl = $page.url.pathname
  $: isHomePage = $page.route.id === '/'
  $: isFullPage = $page.route.id === '/explore'

  function login() {
    logged = !logged
  }
</script>

<div class="min-h-screen flex flex-col dark:bg-gray-900">
  <header
    class="sticky top-0 z-40 w-full bg-white border-b border-gray-200 dark:border-gray-600 dark:bg-gray-800"
  >
    <Navbar let:hidden let:toggle fluid="true" navClass="px-2 py-1 sm:px-4 w-full" >
      <NavBrand href="/">
        <img
        src="{logo}"
        class="mr-3 pt-1 h-12"
        alt="openstreetmap.es"
        />
        <span class="whitespace-nowrap text-2xl font-semibold dark:text-white">
          visor-catastro
        </span>
      </NavBrand>
      <NavUl {hidden} {ulClass} class="order-1">
        <NavLi href="/learn" active={activeUrl.startsWith('/learn')}>Aprende</NavLi>
        <NavLi href="/explore" active={isHomePage}>Explora</NavLi>
      </NavUl>
      <div class="flex md:order-2">
        {#if logged}
          <Button pill color="light" id="avatar-menu" class="!p-0">
            <Chevron>
              <Avatar src="{avatar}" class="mr-2"/>
              <span class="sm:max-md:hidden">Cuenta OSM</span>
            </Chevron>
          </Button>
          <Dropdown placement="bottom" triggeredBy="#avatar-menu">
            <DropdownItem>
              Tema:
              <DarkMode/>
            </DropdownItem>
            <DropdownItem>Ajustes</DropdownItem>
            <DropdownItem on:click={login}>Cerrar sesión</DropdownItem>
          </Dropdown>
        {:else}
          <Button outline size="sm" on:click={login}>Iniciar sesión</Button>
        {/if}
        <NavHamburger on:click={toggle} />
      </div>
    </Navbar>
  </header>

  <slot />
</div>