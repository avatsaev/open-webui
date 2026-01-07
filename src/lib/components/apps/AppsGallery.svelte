<script lang="ts">
	import { toast } from 'svelte-sonner';
	import { onMount, getContext } from 'svelte';

	const i18n = getContext('i18n');

	import { WEBUI_NAME, user, showSidebar } from '$lib/stores';
	import { getActiveApps } from '$lib/apis/apps';

	import Search from '$lib/components/icons/Search.svelte';
	import Spinner from '$lib/components/common/Spinner.svelte';
	import XMark from '$lib/components/icons/XMark.svelte';
	import AppGalleryItem from './AppGalleryItem.svelte';

	let loaded = false;
	let apps: any[] = [];
	let filteredApps: any[] = [];
	let query = '';

	$: {
		if (query) {
			filteredApps = apps.filter(
				(app) =>
					app.title.toLowerCase().includes(query.toLowerCase()) ||
					(app.meta?.description ?? '').toLowerCase().includes(query.toLowerCase())
			);
		} else {
			filteredApps = apps;
		}
	}

	const getAppList = async () => {
		try {
			const res = await getActiveApps(localStorage.token).catch((error) => {
				toast.error(`${error}`);
				return [];
			});

			if (res) {
				apps = res;
				filteredApps = res;
			}
		} catch (err) {
			console.error(err);
		}
	};

	onMount(async () => {
		await getAppList();
		loaded = true;
	});
</script>

<svelte:head>
	<title>
		{$i18n.t('App Gallery')} • {$WEBUI_NAME}
	</title>
</svelte:head>

{#if loaded}
	<div
		class="flex flex-col h-full w-full px-4 py-4 transition-width duration-200 ease-in-out {$showSidebar
			? 'md:max-w-[calc(100%-260px)]'
			: ''} max-w-full"
	>
		<div class="flex flex-col gap-1 mb-4 max-w-6xl mx-auto w-full">
			<div class="flex justify-between items-center">
				<div class="flex items-center text-2xl font-semibold gap-2">
					<div>
						{$i18n.t('App Gallery')}
					</div>
					<div class="text-lg font-medium text-gray-500 dark:text-gray-500">
						{filteredApps.length}
					</div>
				</div>
			</div>

			<p class="text-sm text-gray-500 dark:text-gray-400">
				{$i18n.t('Discover and use apps created by the community')}
			</p>
		</div>

		<div
			class="py-2 bg-white dark:bg-gray-900 rounded-3xl border border-gray-100/30 dark:border-gray-850/30 flex-1 overflow-hidden flex flex-col max-w-6xl mx-auto w-full"
		>
			<div class="px-3.5 flex items-center w-full space-x-2 py-0.5 pb-2">
				<div class="flex flex-1 items-center">
					<div class="self-center ml-1 mr-3">
						<Search className="size-3.5" />
					</div>
					<input
						class="w-full text-sm py-1 rounded-r-xl outline-hidden bg-transparent"
						bind:value={query}
						placeholder={$i18n.t('Search Apps')}
					/>

					{#if query}
						<div class="self-center pl-1.5 translate-y-[0.5px] rounded-l-xl bg-transparent">
							<button
								class="p-0.5 rounded-full hover:bg-gray-100 dark:hover:bg-gray-900 transition"
								on:click={() => {
									query = '';
								}}
							>
								<XMark className="size-3" strokeWidth="2" />
							</button>
						</div>
					{/if}
				</div>
			</div>

			{#if filteredApps.length > 0}
				<div
					class="px-3 my-2 gap-2 grid sm:grid-cols-2 lg:grid-cols-3 overflow-y-auto flex-1 auto-rows-min content-start"
				>
					{#each filteredApps as app (app.id)}
						<AppGalleryItem {app} />
					{/each}
				</div>
			{:else}
				<div class="w-full h-full flex flex-col justify-center items-center my-16 mb-24">
					<div class="max-w-md text-center">
						<div class="text-3xl mb-3">😕</div>
						<div class="text-lg font-medium mb-1">{$i18n.t('No apps found')}</div>
						<div class="text-gray-500 text-center text-xs">
							{$i18n.t('Try adjusting your search to find what you are looking for.')}
						</div>
					</div>
				</div>
			{/if}
		</div>
	</div>
{:else}
	<div class="w-full h-full flex justify-center items-center">
		<Spinner className="size-5" />
	</div>
{/if}
