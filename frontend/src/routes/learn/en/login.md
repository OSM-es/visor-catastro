<script>
  import { Button, Radio, Video } from 'flowbite-svelte'
  import { Check, ChevronRight } from 'svelte-heros-v2'

	import { enhance } from '$app/forms'
  import { goto, invalidate } from '$app/navigation'
  import { login, relogin, signup } from '$lib/user'

  export let user

  const guideUrl = 'https://wiki.openstreetmap.org/wiki/ES:Catastro_espa%C3%B1ol/Importaci%C3%B3n_de_edificios'

  function next() {
    goto('/learn/setup')
  }
</script>

## Import account

To record your steps in this tutorial you must log in with an OSM account.
{#if user}<Check color="green" ariaLabel="Hecho" class="inline"/>{/if}

The OpenStreetMap Community rules state that it is necessary to use a
dedicated account to carry out a data import.
Follow the steps in the <a href={guideUrl} target="_blank">Import Guide</a> or this video (TODO) to
{#if user?.import_id}crearla. <Check color="green" ariaLabel="Hecho" class="inline"/>{:else}<Button color="light">Create an import account</Button>{/if}

It is recommended that the dedicated account is clearly identified containing the term 'import' or 'cadastre'.
{#if user?.stated}<Check color="green" ariaLabel="Hecho" class="inline"/>{/if}

{#if !user}
<Button on:click={login}>Sign in</Button> with the import account.

{:else if user?.import_id && !user?.osm_id}
If you wish, you can <Button on:click={relogin}>link your OSM account</Button> and you will be able to access this site with any of them.

{:else if !user?.import_id && !user?.osm_id}
{user.display_name} is:
<form use:enhance method="POST">
  <Radio name="type" value="import">The account that I will use for the import.</Radio>
  <Radio name="type">The account I normally use in OSM.</Radio>

  <Button type="submit" class="mt-8">Confirm</Button>
</form>

{:else if !user?.import_id}
<Button on:click={relogin}>Link your import account</Button>

{/if}

{#if user?.tutorial?.passed?.includes('login')}
Registration process complete!
<Button color="primary" on:click={next}>
  Continue <ChevronRight/>
</Button>

{/if}