<script lang="ts">
	import { onMount, onDestroy, tick, getContext } from 'svelte';
	import { writable } from 'svelte/store';
	import { goto } from '$app/navigation';
	import { toast } from 'svelte-sonner';
	import { showSidebar } from '$lib/stores';
	import { getAppById } from '$lib/apis/apps';
	import Artifacts from '$lib/components/chat/Artifacts.svelte';
	import { artifactCode, artifactContents } from '$lib/stores';

	const i18n = getContext('i18n');

	let loading = false;
	let mounted = false;
	let app = null;
	export let id = '';
	let history: Array<{ type: string; content: string }> = [];

	const loadApp = async () => {
		loading = true;
		try {
			app = await getAppById(localStorage.token, id);
			if (!app) {
				toast.error($i18n.t('App not found'));
				goto('/');
				return;
			}
			history = [{ type: 'iframe', content: app.source_code }];

			artifactContents.set(history);
			await tick();
		} catch (error) {
			console.error(error);
			toast.error($i18n.t('App not found'));
			goto('/');
			return;
		} finally {
			loading = false;
		}
	};

	onMount(async () => {
		await loadApp();
		mounted = true;
	});

	onDestroy(() => {
		artifactContents.set([]);
	});

	$: if (mounted && id) {
		loadApp();
	}
</script>

<svelte:head>
	<title></title>
</svelte:head>
<div
	class="h-screen max-h-[100dvh] transition-width duration-200 ease-in-out {$showSidebar
		? '  md:max-w-[calc(100%-260px)]'
		: ' '} w-full max-w-full flex flex-col"
	id="chat-container"
>
	<div class="flex-1 h-full relative overflow-hidden">
		{#if loading}
			<p>Loading App...</p>
		{:else if history.length > 0}
			<Artifacts appTitle={app.title} enableAppViewMode={true} />
		{/if}
	</div>
</div>
