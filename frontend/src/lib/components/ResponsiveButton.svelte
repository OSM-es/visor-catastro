<script>
    import {Button, Tooltip } from 'flowbite-svelte'

    export let btnClass = ''
    export let href = undefined
    export let size = 'sm'
    export let title
    export let type = 'button'
    export let name = undefined
    export let value = undefined
    export let placement = 'bottom'
</script>

<Button {type} {name} {value} {size} {href} class={btnClass} on:click>
    <slot></slot>
    <span class="max-lg:hidden ml-1">{title}</span>
</Button>
<Tooltip {placement} class="lg:hidden">{title}</Tooltip>
