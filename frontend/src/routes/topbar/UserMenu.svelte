<script>
  import {
    Avatar,
    Button,
    Chevron,
    Dropdown,
    DropdownItem,
  } from 'flowbite-svelte'

  import { login, logout, signup } from '$lib/user'

  export let user

  const btnClass = '!p-0.5 dark:bg-transparent dark:border-neutral-600 '
    + 'dark:hover:bg-neutral-700 dark:hover:border-neutral-600 !ring-0'
</script>

{#if user}
<Button pill color="light" id="avatar-menu" class={btnClass}>
  <Chevron>
    <Avatar src="{user?.img?.href}" size="sm"/>
    <span class="max-md:hidden ml-2">{user.display_name}</span>
  </Chevron>
</Button>
<Dropdown placement="bottom-end" triggeredBy="#avatar-menu" class="dark:bg-neutral-700">
  <DropdownItem><a href="/settings">Ajustes</a></DropdownItem>
  <DropdownItem on:click={logout}>Cerrar sesión</DropdownItem>
</Dropdown>
{:else}
<Button outline size="sm" color="light" class="max-md:hidden" on:click={signup}>
  Registrarse
</Button>
<Button id="login" outline size="sm" on:click={login}>Iniciar sesión</Button>
{/if}
