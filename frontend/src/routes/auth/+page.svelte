<script>
    /**
     * Redirect page after login.
     */
    import { onMount } from 'svelte'
    import { goto } from '$app/navigation'

    onMount(() => {
        if (window.opener) {
            window.opener.document.getElementById('auth').dispatchEvent(new Event('click'))
            window.close()
        } else {
            goto('/')
        }
    })
</script>