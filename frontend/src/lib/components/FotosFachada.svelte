<script>
  import Viewer2 from 'viewerjs'
  import 'viewerjs/dist/viewer.css'

  import { createEventDispatcher, onMount } from 'svelte'
  import { goto } from '$app/navigation'

  import { FotoFachadaUrl } from '$lib/config'

  const options = {
    navbar: false,
    rotatable: false,
    scalable: false,
    title: [true, (image) => `${image.alt}`],
  }
  const dispatch = createEventDispatcher()

  export let data
  export let scrollImage
  export let viewImage
  
  let viewer
  $: images = getImages(data)
  
  $: document.getElementById(`foto_${scrollImage}`)?.scrollIntoView()
  $: {
    if (viewImage) {
      const index = images.findIndex(im => im.ref === viewImage)
      viewer.view(index)
    }
  }
  
  onMount(() => {
    viewer = new Viewer2(document.getElementById('FotosFachada'), options)
  })

  function getImages(data) {
    const addresses = {}

    for (const feat of data) {
      const tags = feat.properties?.tags || {}
      const ref = tags?.ref
      const number = ('00000' + (tags['addr:housenumber'] || '')).slice(-5)
      let adr = tags['addr:street'] || tags['addr:place'] || ''
      adr += tags['addr:housenumber'] ? `, ${number}` : ''
      if (ref in addresses && adr && !addresses[ref].includes(adr)) {
        addresses[ref] += `; ${adr}`
      } else if (ref && adr) {
        addresses[ref] = adr
      }
    }

    let images = Object.entries(addresses).map(([ref, addrs]) => {
      return { ref, addrs }
    })
    images.sort((first, second) => first.addrs > second.addrs)
    for (const im of images) {
      im.addrs = im.addrs.replace(/ 0+/, ' ')
    }

    return images
  }

  function viewed(event) {
    const ref = event.detail.image.alt.split(' ', 1)[0]
    dispatch('viewed', ref)
  }

  function hidden() {
    goto(document.location.pathname)
  }
</script>

<div id="FotosFachada" on:viewed={viewed} on:hidden={hidden}>
    {#each images as im}
    <div>
      <div>
        <img
          id="foto_{im.ref}"
          src="{FotoFachadaUrl}{im.ref}"
          alt="{im.ref} {im.addrs}"
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
  @media only screen and (max-width: 600px) {
    #FotosFachada div div::after {
      content: '© D.G.Catastro';
    }
  } 

  :global(.viewer-footer .viewer-title) {
    opacity: 100% !important;
    font-size: 16px !important;
    color: white !important;
    background-color: #00000033;
    padding: 0.2em 0.4em;
  }
</style>