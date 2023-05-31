<script>
  import SideBar from './SideBar.svelte'
</script>

<div class="lg:flex">
  <SideBar/>

  <main class="mx-4 mt-8 lg:mx-20">
    <article class="prose md:prose-xl dark:prose-invert">
      <slot/>
    </article>
  </main>
</div>
