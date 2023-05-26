<script>
  import SideBar from './SideBar.svelte'
</script>

<div class="lg:flex">
  <SideBar/>

  <main class="mx-4 mt-8 lg:mx-auto">
    <slot/>
  </main>
</div>
