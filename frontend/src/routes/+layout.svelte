<script>
  import '../app.postcss'
  import { page } from '$app/stores'
  import { login, logout } from '$lib/user'
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

  export let data

  let signupUrl = 'https://www.openstreetmap.org/user/new'
  let ulClass = 'flex flex-col md:flex-row md:space-x-8 items-center order-1 font-medium'
  
  $: user = data.user
  $: activeUrl = $page.url.pathname
  $: isMapPage = $page.url.pathname.startsWith('/explore')

  function signup() {
    const options = 'location=yes,height=950,width=800,scrollbars=yes,status=yes'
    window.open(signupUrl, '_blank', options)
  }
</script>

<div class="h-screen flex flex-col dark:bg-gray-900">
  <header
    class="sticky top-0 z-40 w-full border-b border-gray-200 dark:border-gray-600"
  >
    <Navbar
      let:hidden
      let:toggle
      fluid="true"
      navClass="py-0.5 mx-auto {isMapPage ? 'px-2 sm:px-4 w-full': 'max-w-7xl px-4'}"
    >
      <NavBrand href="/">
        <img
        src="{logo}"
        class="mr-3 pt-1 h-12"
        alt="openstreetmap.es"
        />
        <div class="dark:text-white">
          <p class="text-xs font-medium h-2">visor</p>
          <p class="text-xl font-semibold h-5">catastro</p>
          <p class="text-xs text-right">OSM.es</p>
        </div>
      </NavBrand>
      <NavUl {hidden} {ulClass} class="order-1">
        <NavLi href="/learn" active={activeUrl.startsWith('/learn')}>Aprende</NavLi>
        <NavLi href="/explore" active={isMapPage}>Explora</NavLi>
      </NavUl>
      <div class="flex md:order-2">
        {#if user}
          <Button pill color="light" id="avatar-menu" class="!p-0.5">
            <Chevron>
              <Avatar src="{user.img.href}" size="sm" class="mr-2"/>
              <span class="max-md:hidden">{user.display_name}</span>
            </Chevron>
          </Button>
          <Dropdown placement="bottom" triggeredBy="#avatar-menu">
            <DropdownItem>
              Tema:
              <DarkMode/>
            </DropdownItem>
            <DropdownItem><a href="/settings">Ajustes</a></DropdownItem>
            <DropdownItem on:click={logout}>Cerrar sesión</DropdownItem>
          </Dropdown>
        {:else}
        <Button outline size="sm" color="light" class="max-md:hidden mr-2" on:click={signup}>
          Registrarse
        </Button>
        <Button id="login" outline size="sm" on:click={login}>Iniciar sesión</Button>
        {/if}
        <NavHamburger on:click={toggle} />
      </div>
    </Navbar>
  </header>

  {#if isMapPage}
  <slot/>
  {:else}
  <main class="mx-4 mt-8 lg:mx-auto">
    <slot />
  </main>
  {/if}
</div>
