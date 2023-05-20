<script>
	import { enhance } from '$app/forms'
  import { Button, Input } from 'flowbite-svelte'

  export let data

  let status = ''
  $: user = data.user

  const updateStatus = () => {
    return ({ result, update }) => {
      if (result.type === 'success') {
        status = result.data.status
      } else {
        update()
      }
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
	<form use:enhance={updateStatus} 
    method="POST"
    action="?/save"
  >
    <Input type="email" name="email" placeholder="email" />
    <Button type="submit">Enviar</Button>
	</form>
  <p>{status}</p>
</article>