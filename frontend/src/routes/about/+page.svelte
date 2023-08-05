<script>
  import { Button } from 'flowbite-svelte'
  import { t } from '$lib/translations'

  import banner from '$lib/images/visor-catastro.svg'
  import StatsSection from '$lib/components/StatsSection.svelte'

  export let data
</script>
  
<div class="flex flex-col flex-grow max-w-5xl lg:px-20 px-4 mx-auto mt-8">
  <h2 class="mb-9 text-xl sm:text-4xl font-bold leading-snug text-center text-primary-900 dark:text-white">
    {$t('about.title')}
  </h2>
  <a href="/learn">
    <img src="{banner}" alt="Visor Catastro"/>
  </a>
  <div class="my-16 mx-auto">
    <Button shadow="blue" size="xl" href="/learn">{$t('about.learn')}</Button>
    <Button shadow="blue" size="xl" class="max-sm:hidden ml-16" outline href="/explore">
      {$t('about.start')}
    </Button>
  </div>
  {#await data.streamed.stats}
    <span></span>
  {:then value}
    <StatsSection stats={value} size={'text-5xl'}/>
  {:catch}
    <span></span>
  {/await}
  <div class="bg-gray-100 dark:bg-gray-800 p-4">
    <article class="prose max-w-none lg:prose-xl dark:prose-invert mx-auto">
      <p>
        {$t('about.this')}
        {$t('about.disclaimer')}
      </p> 
      <p>
        {$t('about.goal')}
        <a href="/explore" class="lowercase">{$t('menu.explore')}</a>.
      </p>
      <p>
        {$t('about.contrib')} <a href="https://github.com/OSM-es/visor-catastro/">GitHub</a>.
        {$t('about.contact')} <a href="https://telegram.me/OSMes_Catastro">Telegram</a>.
      </p>
    </article>
  </div>
</div>