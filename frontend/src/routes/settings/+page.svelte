<script>
	import { enhance } from '$app/forms'
  import RelativeTime from 'svelte-relative-time'
  import {
    Avatar,
    Button,
    Card,
    Input,
    Label,
  } from 'flowbite-svelte'

  export let data

  $: user = data.user

  const updateForm = () => {
    return ({ update }) => {
      update({ reset: false })
    }
  }
</script>

<article class="mx-8 mt-8">
	<div class="flex items-center space-x-8 mb-8">
    <Avatar src="{user?.img?.href}" size="xl" rounded/>
    <h2 class="text-xl md:text-2xl font-bold">{user.display_name}</h2>
  </div>
  
  <div class="grid grid-cols-2 gap-8 place-content-stretch">
    <Card padding="xl" size="lg">
      <h5 class="pb-4 text-lg font-medium border-b border-neutral-200 dark:border-neutral-700">Ajustes</h5>
      {#if user.stated}
        <form use:enhance={updateForm} 
          method="POST"
          action="?/save"
          class="pt-8 space-y-4"
        >
          <Label for="email">Correo electrónico</Label>
          <Input id="email" type="email" name="email" value={user.email}/>
          <Button type="submit">Enviar</Button>
        </form>
      {:else}
        <Button href="/learn/login">Completa el tutorial para editar</Button>
      {/if}
    </Card>
    <Card padding="xl" size="md">
      <h5 class="pb-4 text-lg font-medium border-b border-neutral-200 dark:border-neutral-700">Detalles de OpenStreetMap</h5>
      <dl>
        <div class="py-6 grid sm:grid-cols-2 sm:gap-4">
          <dt class="font-medium">
            Cuenta creada
          </dt>
          <dd>
            <RelativeTime date={new Date(user.account_created)}/>
          </dd>
          <dt class="font-medium">
            Conjuntos de cambios
          </dt>
          <dd>
            {user.changesets.count}
          </dd>
        </div>
      </dl>
    </Card>
  </div>
</article>