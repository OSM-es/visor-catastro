<script>
  import { Button, ButtonGroup } from 'flowbite-svelte';
  import banner from '$lib/images/visor-catastro.svg'
</script>
  
<div class="flex flex-col flex-grow max-w-5xl lg:px-20 px-4 mx-auto mt-8">
  <h2 class="mb-9 text-xl sm:text-4xl font-bold leading-snug text-center text-primary-900 dark:text-white">
    Herramienta de gestión de la importación del Catastro Español a OpenStreetMap
  </h2>
  <a href="/learn">
    <img src="{banner}" alt="Visor Catastro"/>
  </a>
  <div class="my-16 mx-auto">
    <Button shadow="blue" size="xl" href="/learn">Aprender más</Button>
    <Button shadow="blue" size="xl" class="max-sm:hidden ml-16" outline href="/explore">
      Comenzar a mapear
    </Button>
  </div>
  <div class="bg-gray-100 dark:bg-gray-800 p-4">
    <article class="prose max-w-none lg:prose-xl dark:prose-invert mx-auto">
      <p>
        Prototipo para la importación directa de los archivos.
        Por el momento es una simple maqueta con la parte de la interacción
        del usuario. No almacena información ni guarda estados de las tareas.
      </p> 
      <p>
        El objetivo es poder colaborar sin pasos intermedios: compruébalo en
        <a href="/explore">explora</a>.
      </p>
      <p>
        Se aceptan contribuciones en <a href="https://github.com/OSM-es/visor-catastro/">GitHub</a>.
        Contacta en <a href="https://telegram.me/OSMes_Catastro">Telegram</a>.
      </p>
    </article>
  </div>
</div>