<script>
  import Viewer2 from 'viewerjs'
  import 'viewerjs/dist/viewer.css'
  import ExifReader from 'exifreader'

  import { createEventDispatcher, onMount } from 'svelte'
  import { afterNavigate, goto } from '$app/navigation'

  import { PUBLIC_API_URL } from '$lib/config'

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
  
  let viewer, images
  
  $: getImages(data)
  $: document.getElementById(`foto_${scrollImage}`)?.scrollIntoView()
  $: {
    if (viewImage) {
      const index = images.findIndex(im => im.ref === viewImage)
      viewer.view(index)
    }
  }
  

  onMount(() => {
    getImages(data)
    viewer = new Viewer2(document.getElementById('FotosFachada'), options)
  })

  afterNavigate(() => {
    for (const i in images) {
      const ref = images[i].ref
      const el = document.getElementById(`foto_${ref}`)
      const alt = el?.getAttribute('alt')
      if (el && !alt.includes('Año:')) {
        getDate(ref).then((year) => {
          if (year) el.setAttribute('alt', alt + '. Año: ' + year)
        })
      }
    }
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

    images = Object.entries(addresses).map(([ref, addrs]) => {
      return { ref, addrs }
    })
    images.sort((first, second) => first.addrs > second.addrs)
    for (const im of images) {
      im.addrs = im.addrs.replace(/ 0+/, ' ')
    }
  }

  function viewed(event) {
    const ref = event.detail.originalImage.id.replace('foto_', '')
    dispatch('viewed', ref)
  }

  function hidden() {
    goto(document.location.pathname)
  }

  async function getDate(ref) {
    const tags = await ExifReader.load(`${PUBLIC_API_URL}/photo/${ref}`)
    const imageDate = tags?.DateTimeOriginal?.description
    return imageDate?.split(':')[0]
  }
</script>

<div id="FotosFachada" on:viewed={viewed} on:hidden={hidden}>
  {#each images as im, i}
    <div class="text-gray-900 dark:text-gray-100">
      <div>
        <img
          id="foto_{im.ref}"
          src="{PUBLIC_API_URL}/photo/{im.ref}"
          alt="{im.addrs ? im.addrs : im.ref}"
        />
      </div>
      <p class="mt-0 mb-2 text-sm">{im.addrs ? im.addrs : im.ref}</p>
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