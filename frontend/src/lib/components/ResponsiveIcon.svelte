<script>
    import {Tooltip } from 'flowbite-svelte'

    export let title
    export let max = 'max-lg'
    export let min = 'lg'
    export let placement = 'bottom'
</script>

<div class="flex flex-row items-center">
    <slot></slot>
    {#if max === 'md:max-lg'}
        <span class="md:max-lg:hidden ml-1">{title}</span>
    {:else}
        <span class={`${max}:hidden ml-1`}>{title}</span>
    {/if}
</div>
<Tooltip {placement} class={`${min}:hidden`}>{title}</Tooltip>
