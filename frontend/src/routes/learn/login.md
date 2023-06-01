<script>
  import { Button, Radio, Video } from 'flowbite-svelte'
  import { Check, ChevronRight } from 'svelte-heros-v2'

	import { enhance } from '$app/forms'
  import { goto } from '$app/navigation'
  import { login, signup } from '$lib/user'

  export let user

  function isStated() {
    return user?.display_name.includes('import') ||  user?.display_name.includes('catastro')
  }

  function next() {
    goto('/learn/login')
  }
</script>

## Cuenta de importación

Para registrar tus pasos en este tutorial debes iniciar sesión con una cuenta de OSM.
{#if user}<Check color="green" ariaLabel="Hecho" class="inline"/>{/if}

Las normas de la Comunidad OpenStreetMap establecen que es necesario
usar una cuenta dedicada para llevar a cabo una importación de datos.
Sigue los pasos de la Guía de importación o este vídeo para
{#if user?.user?.import_id || isStated()}crearla. <Check color="green" ariaLabel="Hecho" class="inline"/>{:else}<Button color="light">crear una cuenta de importación</Button>{/if}

Es recomendable que la cuenta dedicada este claramente identificada conteniendo el término 'import' o 'catastro'.
{#if isStated()}<Check color="green" ariaLabel="Hecho" class="inline"/>{/if}

{#if user && user.user?.import_id && !user?.user?.osm_id}
Si lo deseas, puedes <Button>asociar tu cuenta OSM</Button> y podrás acceder a este sitio con cualquiera de ellas.

{/if}

{#if user && !user.user?.import_id && !user?.user?.osm_id && !isStated()}
{user.display_name} es:
<form use:enhance method="POST">
<Radio name="type" value="import">La cuenta que voy a utilizar para la importación.</Radio>
<Radio name="type">La cuenta que utilizo normalmente en OSM.</Radio>

<Button type="submit">Confirmar</Button>
</form>

{/if}

{#if !user?.user?.import_id}
<Button>inicia sesion con ella</Button>

{/if}

{#if user?.user?.tutorial?.includes('login')}
Proceso de registro completo
<Button color="primary" on:click={next}>
  Continuar <ChevronRight/>
</Button>

{/if}