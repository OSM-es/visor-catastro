<script>
	import { enhance } from '$app/forms'
  import RelativeTime from 'svelte-relative-time'
  import {
    Avatar,
    Button,
    Card,
    Helper,
    Input,
    Label,
  } from 'flowbite-svelte'

  import { t } from '$lib/translations'
  import LocaleMenu from '$lib/components/LocaleMenu.svelte'

  export let data
  export let form

  $: user = data.user

  const updateForm = () => {
    return ({ update }) => {
      update({ reset: false })
    }
  }
</script>

{#if user}
<article class="mx-8 mt-8">
	<div class="flex items-center space-x-8 mb-8">
    <Avatar src="{user?.img?.href}" size="xl" rounded/>
    <div>
      <h1 class="text-2xl md:text-3xl font-bold mb-4">{user.display_name}</h1>
      <p class="text-lg">{$t('common.' + user.mapping_level)}</p>
    </div>
  </div>
  
  <div class="grid grid-cols-2 gap-8 place-content-stretch">
    <Card padding="xl" size="lg">
      <h5 class="pb-4 text-lg font-medium border-b border-neutral-200 dark:border-neutral-700">
        {$t('settings.settings')}
      </h5>
      <form use:enhance={updateForm} 
        method="POST"
        action="?/save"
        class="pt-8 space-y-4"
      >
        <div class="flex flex-row w-full items-center place-content-between gap-8">
          <Label>{$t('settings.locale')}</Label>
          <div class="w-48"><LocaleMenu/></div>
        </div>
        {#if user.stated}
          <Label for="email" color={form?.errors?.email ? 'red' : 'gray'}>
            {$t('settings.email')}
          </Label>
          <Input id="email" type="email" name="email" value={user.email}/>
          <Helper color="red">{form?.errors?.email || ''}</Helper>
          {#if !form?.errors}
            <Helper>
              {$t('settings.privacy')}
            </Helper>
          {/if}
          <Button type="submit">{$t('common.send')}</Button>
        {:else}
          <Button href="/learn/login">
            {$t('common.dotutorial', { action: $t('common.edit') })}
          </Button>
        {/if}
      </form>
    </Card>
    <Card padding="xl" size="md">
      <h5 class="pb-4 text-lg font-medium border-b border-neutral-200 dark:border-neutral-700">
        {$t('settings.osmdetails')}
      </h5>
      <dl>
        <div class="py-6 grid sm:grid-cols-2 sm:gap-4">
          <dt class="font-medium">
            {$t('settings.accountcreated')}
          </dt>
          <dd>
            <RelativeTime date={new Date(user.account_created)} locale={'es-ES'}/>
          </dd>
          <dt class="font-medium">
            {$t('settings.changesets')}
          </dt>
          <dd>
            {user.changesets.count}
          </dd>
        </div>
      </dl>
    </Card>
  </div>
</article>
{/if}