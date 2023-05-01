<script>
  import { Button, ButtonGroup } from 'flowbite-svelte';
  import banner from '$lib/images/visor-catastro.svg'
</script>
  
<div class="flex flex-col flex-grow max-w-6xl lg:px-20 px-4 mx-auto mt-8">
  <h2 class="mb-6 text-4xl font-bold leading-snug text-center text-primary-900 dark:text-white">
    Herramienta de gestión de la importación del Catastro Español a OpenStreetMap
  </h2>
  <a href="/learn">
    <img src="{banner}" alt="Visor Catastro"/>
  </a>
  <div class="my-16 mx-auto">
    <Button shadow="blue" size="xl" class="mr-16" href="/learn">Aprender más</Button>
    <Button shadow="blue" size="xl" outline href="/explore">Comenzar a mapear</Button>
  </div>
  <article class="prose lg:prose-xl dark:prose-invert">
    <p>Prototipo para la importación directa de los archivos.</p> 
    <p>
      El objetivo es poder colaborar sin pasos intermedios: en
      <a href="/explora">explora</a>, acercarse al sitio
      que se desee importar, seleccionar una parcela y mapearla.
    </p>
    <p>
      Por el momento esto es una simple maqueta con la parte de la interacción
      del usuario. No almacena información ni guarda estados de las parcelas.
    </p>
  </article>
</div>