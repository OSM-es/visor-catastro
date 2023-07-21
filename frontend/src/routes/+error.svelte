<script>
  import { FaceFrown } from 'svelte-heros-v2'
  import { page } from '$app/stores';
</script>

<div class="flex items-center justify-center flex-grow">
  <div class="flex flex-col md:flex-row items-start md:items-center space-y-3 space-x-3">
    <p class="font-semibold text-red-500 text-9xl">
      {$page.status}
    </p>
    <div class="space-y-2">
      <h1 class="flex items-center space-x-2">
        <FaceFrown class="text-red-500"/>
        <span class="text-xl font-medium">
          {$page.error.message}
        </span>
      </h1>
      <p>
        {#if $page.status === 404}
          No se encontró la página que estás buscando.
        {:else}
          Se ha producido un problema.
        {/if}
      </p>
      <p>
        Regresa a la
        <a href="/" class="text-blue-600 hover:underline dark:text-blue-500">página principal</a>
      </p>
    </div>
  </div>
</div>
