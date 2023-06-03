<script>
    /**
     * Redirect page after login.
     */
    import { onMount } from 'svelte'
    import { goto } from '$app/navigation'

    onMount(() => {
        if (window.opener) {
            const usermenu = window.opener.document.getElementById('usermenu')
            usermenu.dispatchEvent(new CustomEvent('invalidateuser'))
            window.close()
        } else {
            goto('/')
        }
    })
</script>