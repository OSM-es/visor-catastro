<script>
  import { CloseButton, Sidebar, SidebarWrapper } from 'flowbite-svelte'

	import { getContext } from 'svelte'
  import { afterNavigate } from '$app/navigation'

  const drawerHiddenStore = getContext('drawer')

  function closeDrawer() {
    drawerHiddenStore.set(true)
  }

  afterNavigate(closeDrawer)
</script>

<Sidebar
	asideClass="fixed inset-0 z-30 flex-none h-full w-1/4 lg:static lg:h-auto bg-slate-100 border-r border-gray-300 dark:border-gray-600 lg:overflow-y-visible lg:block"
	class="{$drawerHiddenStore && 'hidden'}"
>
	<SidebarWrapper divClass="overflow-y-auto bg-inherit w-64 ml-auto pl-4 pr-1 pt-16 lg:pt-6 h-full scrolling-touch lg:h-[calc(100vh-4rem)] lg:block lg:mr-0 lg:sticky top-14">
		<nav>
			<ul>
				<li><a href="">blablablabla</a></li>
				<li><a href="">blablabla</a></li>
				<li><a href="">blabla</a></li>
				<li><a href="" class="active">blablablabla</a></li>
				<li><a href="">blablablabla</a></li>
				<li><a href="">blablablabla</a></li>
			</ul>
		</nav>
	</SidebarWrapper>
</Sidebar>

<div
	hidden={$drawerHiddenStore}
	class="fixed inset-0 z-20 bg-gray-900/50 dark:bg-gray-200/50 text-right pt-16 pr-3"
	on:click={closeDrawer}
	on:keydown={closeDrawer}
>
	<CloseButton name="Cierra tabla de contenido" class="dark:text-white"/>
</div>

<style>
	nav a {
		color: rgb(55, 65, 81);
	}
	nav a:hover {
		text-decoration: underline;
	}

	nav a.active {
		font-weight: bold;
	}

	nav a.active::after {
		float:right;
		content: url('data:image/svg+xml;utf8,<svg width="24" height="24" xmlns="http://www.w3.org/2000/svg"><g><path fill="black" d="M4,11V13H16L10.5,18.5L11.92,19.92L19.84,12L11.92,4.08L10.5,5.5L16,11H4Z" /></g></svg>');
	}
</style>