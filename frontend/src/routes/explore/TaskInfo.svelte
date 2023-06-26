<script>
  export let task

  import { TASK_TYPE_VALUES, TASK_DIFFICULTY_VALUES, TASK_STATUS_VALUES } from '$lib/config'
</script>

<div class="prose lg:prose-xl dark:prose-invert">
  <ul>
    <li>Código de municipio: {task.properties.muncode}</li>
    <li>Referencia: {task.properties.localid}</li>
    <li>Tipo: {TASK_TYPE_VALUES[task.properties.type]}</li>
    <li>Dificultad: {TASK_DIFFICULTY_VALUES[task.properties.difficulty]}</li>
    <li>Estado: {TASK_STATUS_VALUES[task.properties.status]}</li>
  </ul>
</div>
