<script>
  import { Button, Video } from 'flowbite-svelte'
  import { ChevronRight } from 'svelte-heros-v2'

  import { goto } from '$app/navigation'

  export let user

  function next() {
    goto('/learn/login')
  }
</script>

## Introduction

The Spanish OpenStreetMap community develops an import project
of the Cadastre. The goal is to add buildings and addresses in the parts of the
map where they are not present or improve the data if they already exist.

Watch this video to learn about the project.

<Video src="/src/lib/videos/1intro-catastro.webm" controls trackSrc="1intro-catastro.webm" />

{#if !user}
Learn how to register to participate.

{/if}
<Button color="primary" on:click={next}>
  Continue <ChevronRight/>
</Button>
