<script>
  import { Button, Radio, Video } from 'flowbite-svelte'
  import { Check, ChevronRight } from 'svelte-heros-v2'

	import { enhance } from '$app/forms'
  import { goto, invalidate } from '$app/navigation'
  import { login, relogin, signup } from '$lib/user'

  export let user

  const guideUrl = 'https://wiki.openstreetmap.org/wiki/ES:Catastro_espa%C3%B1ol/Importaci%C3%B3n_de_edificios'

  function next() {
    goto('/learn/login')
  }
</script>

## Cuenta de importación

Para registrar tus pasos en este tutorial debes iniciar sesión con una cuenta de OSM.
{#if user}<Check color="green" ariaLabel="Hecho" class="inline"/>{/if}

Las normas de la Comunidad OpenStreetMap establecen que es necesario
usar una cuenta dedicada para llevar a cabo una importación de datos.
Sigue los pasos de la <a href={guideUrl} target="_blank">Guía de importación</a> o este vídeo (TODO) para
{#if user?.user?.import_id}crearla. <Check color="green" ariaLabel="Hecho" class="inline"/>{:else}<Button color="light">Crear una cuenta de importación</Button>{/if}

Es recomendable que la cuenta dedicada este claramente identificada conteniendo el término 'import' o 'catastro'.
{#if user?.stated}<Check color="green" ariaLabel="Hecho" class="inline"/>{/if}

{#if !user}
<Button on:click={login}>Inicia sesión</Button> con la cuenta de importación.

{:else if user.user?.import_id && !user?.user?.osm_id}
Si lo deseas, puedes <Button on:click={relogin}>vincular tu cuenta OSM</Button> y podrás acceder a este sitio con cualquiera de ellas.

{:else if !user.user?.import_id && !user?.user?.osm_id}
{user.display_name} es:
<form use:enhance method="POST">
  <Radio name="type" value="import">La cuenta que voy a utilizar para la importación.</Radio>
  <Radio name="type">La cuenta que utilizo normalmente en OSM.</Radio>

  <Button type="submit" class="mt-8">Confirmar</Button>
</form>

{:else if !user.user?.import_id}
<Button on:click={relogin}>Vincula tu cuenta de importación</Button>

{/if}

{#if user?.user?.tutorial?.includes('login')}
¡Proceso de registro completo!
<Button color="primary" on:click={next}>
  Continuar <ChevronRight/>
</Button>

{/if}