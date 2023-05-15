<script>
    /**
     * Redirect page after login.
     */
    import { onMount } from 'svelte'
    import { goto } from '$app/navigation'

    onMount(() => {
        if (window.opener) {
            const login = window.opener.document.getElementById('login')
            login.dispatchEvent(new CustomEvent('click', {detail: '/auth'}))
            window.close()
        } else {
            goto('/')
        }
    })
</script>