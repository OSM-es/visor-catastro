<script>
    export let user
</script>

## Preparación

{#if user?.user?.tutorial?.passed?.includes('login')}
El tutorial contendrá más contenido interactivo desarrollando la guía de
importación.

Al completarlo se consigue el nivel para [comenzar a mapear](/explore).

{:else}
Completa el [registro](/learn/login)

{/if}