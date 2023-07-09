<script>
    import {Tooltip } from 'flowbite-svelte'

    export let title
    export let max = 'max-lg'
    export let min = 'lg'
    export let placement = 'bottom'
</script>

<div class="flex flex-row items-center">
    <slot></slot>
    <span class={`${max}:hidden ml-1`}>{title}</span>
</div>
<Tooltip {placement} class={`${min}:hidden`}>{title}</Tooltip>
