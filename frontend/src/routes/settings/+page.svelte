<script>
	import { enhance } from '$app/forms'
  import { Button, Input } from 'flowbite-svelte'

  export let data
	export let form

  $: user = data.user

  const updateForm = () => {
    return ({ update }) => {
      update({ reset: false })
    }
  }
</script>

<article class="prose lg:prose-xl dark:prose-invert">
	<h1>Página protegida</h1>
	<img src="{ user.img.href }" class="w-32" alt="avatar"/>
	<ul>
    <li>{user.display_name}</li>
    <li>Antiguedad: {user.account_created}</li>
    <li>Ediciones: {user.changesets.count}</li>
    <li>Mensajes sin leer: {user.messages.received.unread}</li>
	</ul>
	<form use:enhance={updateForm} 
    method="POST"
    action="?/save"
  >
    <Input
      type="email"
      name="email"
      value={form?.email ?? ''}
    />
    <Button type="submit">Enviar</Button>
	</form>
  <p>{form?.status ?? ''}</p>
</article>