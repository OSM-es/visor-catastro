<script>
  import { Modal } from 'flowbite-svelte'

  export let open = false
  export let alertMessage = ""
</script>

<Modal title="Error" bind:open={open} autoclose outsideclose>
  <p>{alertMessage}</p>
</Modal>