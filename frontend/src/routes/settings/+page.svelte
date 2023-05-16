<script>
    export let data

    let user = data.user
</script>
<h1>Página protegida</h1>
<img src="{user.img.href}" class="w-32" alt="avatar"/>
<ul>
    <li>{user.display_name}</li>
    <li>Antiguedad: {user.account_created}</li>
    <li>Ediciones: {user.changesets.count}</li>
    <li>Mensajes sin leer: {user.messages.received.unread}</li>
</ul>