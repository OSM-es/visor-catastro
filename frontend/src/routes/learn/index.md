<script>
  import { Button, Video } from 'flowbite-svelte'
  import { ChevronRight } from 'svelte-heros-v2'

  import { goto } from '$app/navigation'

  export let user

  function next() {
    goto('/learn/login')
  }
</script>

## Introducción

La comunidad española de OpenStreetMap desarrolla un proyecto de importación
del Catastro. Su objetivo es añadir edificios y direcciones en las partes del
mapa donde no están presentes o mejorar los datos si ya existen.

Visualiza este vídeo para conocer el proyecto.

<Video src="/src/lib/videos/1intro-catastro.webm" controls trackSrc="1intro-catastro.webm" />

Conoce como debes registrarte para participar
<Button color="primary" on:click={next}>
  Continuar <ChevronRight/>
</Button>
