<script>
  import Viewer2 from 'viewerjs'
  import 'viewerjs/dist/viewer.css'

  import { createEventDispatcher, onMount } from 'svelte'

  const urlFF = 'http://ovc.catastro.meh.es/OVCServWeb/OVCWcfLibres/OVCFotoFachada.svc/RecuperarFotoFachadaGet?ReferenciaCatastral='
  const options = {
    navbar: false,
    rotatable: false,
    scalable: false,
    title: [true, (image) => `${image.alt}`],
  }
  const dispatch = createEventDispatcher()

  export let images
  export let scrollImage
  export let viewImage
  
  $: document.getElementById(`foto_${scrollImage}`)?.scrollIntoView()
  $: {
    console.info('view', viewImage)
  }

  onMount(() => {
    const viewer = new Viewer2(document.getElementById('FotosFachada'), options)
  })

  function showBuilding(event) {
    const ref = event.detail.image.alt.split(' ', 1)[0]
    dispatch('showBuilding', ref)
  }

</script>

<div id="FotosFachada" on:viewed={showBuilding}>
    {#each images as im}
    <div>
      <div>
        <img
          id="foto_{im.ref}"
          src="{urlFF}{im.ref}"
          alt="{im.ref} {im.addrs || 'N/D'}"
        />
      </div>
      <p class="mt-0 mb-2 text-sm">{im.ref} {im.addrs}</p>  
    </div>
  {/each}
</div>

<style>
  #FotosFachada div div {
    display: block;
    position: relative;
  }
  #FotosFachada img {
    border: 1px solid gray;
    cursor: zoom-in;
  }
  #FotosFachada div div::after {
    content: '© Dirección General del Catastro';
    background-color: #80808080;
    padding: 0 0.5em 0 0.5em;
    color: white;
    font-size: xx-small;
    position: absolute;
    right: 0;
    bottom: 0;
  }
  
  :global(.viewer-footer .viewer-title) {
    opacity: 100% !important;
    font-size: 16px !important;
    color: white !important;
    background-color: #00000033;
    padding: 0.2em 0.4em;
  }

  :global(.viewer-backdrop) {
    background-color: rgba(0, 0, 0, 0.7) !important;
  }
</style>