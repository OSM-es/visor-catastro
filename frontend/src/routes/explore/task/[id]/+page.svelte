<script>
  import { Button, Input } from 'flowbite-svelte'
  import { goto } from '$app/navigation'

  import { login } from '$lib/user'
  import Map from '$lib/Map.svelte'

  export let data

  let map
  let value = data.task.status
  let geoJsonData = data.task.content

  function exit() {
    const zoom = map.getMap().getZoom() - 1
    const center = map.getMap().getCenter()
    const lat = center.lat.toFixed(4)
    const lng = center.lng.toFixed(4)

    goto(`/explore?map=${zoom}/${lat}/${lng}`)
  }
</script>

<div class="flex flex-col md:flex-row flex-grow">
  <div class="w-full flex-grow z-0">
    <Map bind:map geoJsonData={geoJsonData}/>
  </div>
  <div class="md:max-w-md w-full flex-grow overflow-scroll px-4 pt-8 border-l-2 border-gray-200 dark:border-gray-600">
    <div class="h-full max-h-0">
      <div class="prose lg:prose-xl dark:prose-invert">
        <ul>
          <li>Catastro de {data.task.muncode}</li>
          <li>Referencia: {data.task.localId}</li>
          <li>Tipo: {data.task.type}</li>
          <li>Partes de edificio: {data.task.parts}</li>
          {#if data.user}
            <li>
              Estado:
              <Input type=number bind:value min=0 max=9 />
            </li>
            <Button on:click={exit} color="alternative">Cancelar</Button>
            <Button>Guardar</Button>
          {:else}
            <Button on:click={login}>Registrate para editar</Button>
          {/if}
        </ul>
      </div>
    </div>
  </div>
</div>
