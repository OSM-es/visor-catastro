<script>
  export let progress = '50'
  export let progress2 = '0'
  export let size = 'h-2.5'
  export let color = 'gray'
  export let color2 = 'primary'
  export let divClass = 'w-full bg-gray-200 rounded-full dark:bg-gray-700'

  $: _progress2 = 100 * progress2 / progress

  const barColors = {
    primary: 'bg-primary-600',
    blue: 'bg-blue-600',
    gray: 'bg-gray-600 dark:bg-gray-300',
    red: 'bg-red-600 dark:bg-red-500',
    green: 'bg-green-600 dark:bg-green-500',
    yellow: 'bg-yellow-400',
    purple: 'bg-purple-600 dark:bg-purple-500',
    indigo: 'bg-indigo-600 dark:bg-indigo-500'
  }
</script>

<div class={divClass + ' ' + size}>
  <div class={barColors[color] + ' ' + size + ' rounded-full'} style="width: {progress}%">
    <div class={barColors[color2] + ' ' + size + ' rounded-full'} style="width: {_progress2}%" />
  </div>
</div>
