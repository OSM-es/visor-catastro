<script>
    export let user
</script>

## Setup

{#if user?.tutorial?.passed?.includes('login')}
TODO: The tutorial will contain more interactive content developing the import guide.

When you complete it, you get the level for [start mapping](/explore).

{:else}
Complete the [login tutorial](/learn/login)

{/if}