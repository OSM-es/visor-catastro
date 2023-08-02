<script>
  import FormattedNumber from "$lib/components/FormattedNumber.svelte"

  export let stats
</script>

<div class="flex space-x-8 mb-16">
  <div class="flex-grow text-center">
    <p class="text-red-500 text-4xl font-extrabold">
      <FormattedNumber value={stats?.buildings}/>
    </p>
    <p>Edificios mapeados</p>
  </div>
  <div class="flex-grow text-center">
    <p class="text-red-500 text-4xl font-extrabold">
      <FormattedNumber value={stats?.addresses}/>
    </p>
    <p>Direcciones mapeadas</p>
  </div>
  <div class="flex-grow text-center">
    <p class="text-red-500 text-4xl font-extrabold">
      <FormattedNumber value={stats?.users}/>
    </p>
    <p>Mapeadores totales</p>
  </div>
  <div class="flex-grow text-center">
    <p class="text-red-500 text-4xl font-extrabold">
      <FormattedNumber value={stats?.mappers}/>
    </p>
    <p>Mapeadores en línea</p>
  </div>
</div>