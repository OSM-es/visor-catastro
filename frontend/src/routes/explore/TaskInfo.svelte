<script>
  export let task
</script>

<div class="prose lg:prose-xl dark:prose-invert">
  <ul>
    <li>Código de municipio: {task.properties.muncode}</li>
    <li>Referencia: {task.properties.localid}</li>
    <li>Tipo: {task.properties.type}</li>
    <li>Dificultad: {task.properties.difficulty}</li>
    <li>Estado: {task.properties.status}</li>
  </ul>
</div>
