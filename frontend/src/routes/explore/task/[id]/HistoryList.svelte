<script>
  import { Avatar, Badge, Listgroup, Tooltip } from 'flowbite-svelte'
  import { Clock } from 'svelte-heros-v2'
  import RelativeTime from 'svelte-relative-time'

  import { t } from '$lib/translations'

  export let items
</script>

{#if items?.length}
  <Listgroup {items} let:item>
    <div class="flex items-center space-x-4">
      <Avatar src={item.avatar} data-name={item.user}/>
      <p>
        {$t('task.' + item.action)}
        {$t('task.' + item.text)}
        {#if item.addresses != item.buildings}
          {item.buildings ? $t('explore.buildings') : $t('explore.addresses')}
        {/if}
        <Badge color="black" border>
          <Clock size=14 variation="solid" class="mr-1"/>
          <RelativeTime date={new Date(item.date)} locale={'es-ES'}/>
        </Badge>
      </p>
    </div>
  </Listgroup>
  <Tooltip triggeredBy="[data-name]" on:show={e => name = e.target.dataset.name}>
    {name}
  </Tooltip>
{:else}
  <div class="prose dark:prose-invert pt-4">
    <p>{$t('task.nohistory')}</p>
  </div>
{/if}
