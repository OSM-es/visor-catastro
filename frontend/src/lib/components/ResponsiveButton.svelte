<script>
	import { createEventDispatcher } from 'svelte'

    import {Button, Tooltip } from 'flowbite-svelte'

    export let btnClass
    export let href
    export let size
    export let title
    export let type

    const dispatch = createEventDispatcher()
</script>

<Button {type} {size} {href} class={btnClass} on:click={() => dispatch('click')}>
    <slot></slot>
    <span class="max-lg:hidden ml-1">{title}</span>
</Button>
<Tooltip placement="bottom" class="lg:hidden">{title}</Tooltip>
