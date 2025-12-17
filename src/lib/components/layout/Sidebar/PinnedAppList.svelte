<script>
	import Sortable from 'sortablejs';

	import { onDestroy, onMount, tick } from 'svelte';
	import { goto } from '$app/navigation';

	import { chatId, config, mobile, settings, showSidebar } from '$lib/stores';
	import { WEBUI_BASE_URL } from '$lib/constants';
	import { updateUserSettings } from '$lib/apis/users';
	import { getAppById } from '$lib/apis/apps';
	import PinnedAppItem from './PinnedAppItem.svelte';

	export let selectedChatId = null;
	export let shiftKey = false;

	let pinnedApps = [];
	let apps = [];

	const initPinnedAppsSortable = () => {
		const pinnedAppsList = document.getElementById('pinned-apps-list');
		if (pinnedAppsList && !$mobile) {
			new Sortable(pinnedAppsList, {
				animation: 150,
				onUpdate: async (event) => {
					const appId = event.item.dataset.id;
					const newIndex = event.newIndex;

					const pinnedApps = $settings.pinnedApps;
					const oldIndex = pinnedApps.indexOf(appId);

					pinnedApps.splice(oldIndex, 1);
					pinnedApps.splice(newIndex, 0, appId);

					settings.set({ ...$settings, pinnedApps: pinnedApps });
					await updateUserSettings(localStorage.token, { ui: $settings });
				}
			});
		}
	};

	const loadApps = async () => {
		if (!pinnedApps || pinnedApps.length === 0) {
			apps = [];
			return;
		}

		const loadedApps = [];
		for (const appId of pinnedApps) {
			try {
				const app = await getAppById(localStorage.token, appId);
				if (app) {
					loadedApps.push(app);
				}
			} catch (error) {
				console.error(`Failed to load app ${appId}:`, error);
			}
		}
		apps = loadedApps;
	};

	let unsubscribeSettings;

	onMount(async () => {
		pinnedApps = $settings?.pinnedApps ?? [];

		if (pinnedApps.length === 0 && $config?.default_pinned_apps) {
			const defaultPinnedApps = ($config?.default_pinned_apps).split(',').filter((id) => id);
			pinnedApps = defaultPinnedApps;

			settings.set({ ...$settings, pinnedApps });
			await updateUserSettings(localStorage.token, { ui: $settings });
		}

		await loadApps();

		unsubscribeSettings = settings.subscribe(async (value) => {
			const newPinnedApps = value?.pinnedApps ?? [];
			if (JSON.stringify(newPinnedApps) !== JSON.stringify(pinnedApps)) {
				pinnedApps = newPinnedApps;
				await loadApps();
			}
		});

		await tick();
		initPinnedAppsSortable();
	});

	onDestroy(() => {
		if (unsubscribeSettings) {
			unsubscribeSettings();
		}
	});
</script>

<div class="mt-0.5 pb-1.5" id="pinned-apps-list">
	{#each apps as app (app.id)}
		<PinnedAppItem
			{app}
			{shiftKey}
			onClick={(e) => {
				e.preventDefault();
				selectedChatId = null;
				chatId.set('');
				goto(`/apps/${encodeURIComponent(app.id)}`);
				if ($mobile) {
					showSidebar.set(false);
				}
			}}
			onUnpin={($settings?.pinnedApps ?? []).includes(app.id)
				? async () => {
						const pinnedApps = $settings.pinnedApps.filter((id) => id !== app.id);
						settings.set({ ...$settings, pinnedApps });
						await updateUserSettings(localStorage.token, { ui: $settings });
					}
				: null}
		/>
	{/each}
</div>
