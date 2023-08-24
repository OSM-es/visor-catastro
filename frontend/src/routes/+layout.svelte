<script>
  import { page } from '$app/stores'
  import { navigating } from '$app/stores'
  import { derived } from "svelte/store"
    
  import '../app.postcss'
  import Topbar from './topbar/TopBar.svelte'
  
  export let data

  let timer = null

  const navigationIsDelayed = derived(navigating, (newValue, set) => {
    if (timer) clearTimeout(timer)
    if (newValue) {
      timer = setTimeout(() => set(true), 500)
    }
    set(false)
  })
</script>

<div class="min-h-screen flex flex-col dark:bg-neutral-900 dark:text-neutral-100">
  <header
    class="sticky top-0 z-40 w-full drop-shadow-md"
  >
    <Topbar user={data.user}/>
  </header>
  {#if $navigationIsDelayed}
    <div class="wrapper">
      <div class="loader">
        <div></div>
        <div></div>
        <div></div>
        <div></div>
        <div></div>
        <div></div>
        <div></div>
        <div></div>
        <div></div>
      </div>
    </div>
  {/if}

  <slot/>
</div>

<style lang="sass">
  $boxes: 10
  $durationAll: .8s
  $duration: calc(-1 * $durationAll / $boxes)
  $color: #2563eb

  .wrapper
    position: fixed
    left: 0
    right: 0
    bottom: 0
    top: 52px
    width: h-full
    height: 3px
    z-index: 500
    
  .loader
    height: 100%
    display: flex
    transform: translateZ(0)
    
    div
      flex: 1
      background: #{$color}
      animation: go #{$durationAll} infinite alternate ease
      box-shadow: 0 0 10px #{$color}
      
      @for $i from 1 through $boxes
        &:nth-child(#{$i})
          animation-delay: $duration * ($boxes - $i)
      
  @keyframes go
    100%
      background: transparent
      flex: 10
      box-shadow: 0 0 0 transparent
</style>