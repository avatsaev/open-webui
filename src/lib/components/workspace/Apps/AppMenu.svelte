<script lang="ts">
	import { DropdownMenu } from 'bits-ui';
	import { flyAndScale } from '$lib/utils/transitions';
	import { getContext } from 'svelte';

	import Dropdown from '$lib/components/common/Dropdown.svelte';
	import GarbageBin from '$lib/components/icons/GarbageBin.svelte';
	import Pencil from '$lib/components/icons/Pencil.svelte';
	import Tooltip from '$lib/components/common/Tooltip.svelte';
	import Share from '$lib/components/icons/Share.svelte';
	import DocumentDuplicate from '$lib/components/icons/DocumentDuplicate.svelte';
	import Download from '$lib/components/icons/Download.svelte';
	import Link from '$lib/components/icons/Link.svelte';
	import Eye from '$lib/components/icons/Eye.svelte';
	import EyeSlash from '$lib/components/icons/EyeSlash.svelte';

	import { config, user as currentUser, settings } from '$lib/stores';
	import { updateUserSettings } from '$lib/apis/users';

	const i18n = getContext('i18n');

	export let user;
	export let app;

	export let editHandler: Function;
	export let shareHandler: Function;
	export let cloneHandler: Function;
	export let exportHandler: Function;
	export let copyLinkHandler: Function;
	export let deleteHandler: Function;
	export let onClose: Function;

	let show = false;

	const pinAppHandler = async (appId) => {
		let pinnedApps = $settings?.pinnedApps ?? [];

		if (pinnedApps.includes(appId)) {
			pinnedApps = pinnedApps.filter((id) => id !== appId);
		} else {
			pinnedApps = [...new Set([...pinnedApps, appId])];
		}

		settings.set({ ...$settings, pinnedApps: pinnedApps });
		await updateUserSettings(localStorage.token, { ui: $settings });
	};
</script>

<Dropdown
	bind:show
	on:change={(e) => {
		if (e.detail === false) {
			onClose();
		}
	}}
>
	<Tooltip content={$i18n.t('More')}>
		<button
			on:click={(e) => {
				e.stopPropagation();
				show = !show;
			}}
		>
			<slot />
		</button>
	</Tooltip>

	<div slot="content">
		<DropdownMenu.Content
			class="w-full max-w-[170px] rounded-2xl p-1 border border-gray-100  dark:border-gray-800 z-50 bg-white dark:bg-gray-850 dark:text-white shadow-lg"
			sideOffset={-2}
			side="bottom"
			align="start"
			transition={flyAndScale}
		>
			<DropdownMenu.Item
				type="button"
				aria-pressed={($settings?.pinnedApps ?? []).includes(app?.id)}
				class="flex gap-2 items-center px-3 py-1.5 text-sm  cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800 rounded-xl"
				on:click={(e) => {
					e.stopPropagation();
					e.preventDefault();
					pinAppHandler(app?.id);
					show = false;
				}}
			>
				{#if ($settings?.pinnedApps ?? []).includes(app?.id)}
					<EyeSlash />
				{:else}
					<Eye />
				{/if}

				<div class="flex items-center">
					{#if ($settings?.pinnedApps ?? []).includes(app?.id)}
						{$i18n.t('Hide from Sidebar')}
					{:else}
						{$i18n.t('Keep in Sidebar')}
					{/if}
				</div>
			</DropdownMenu.Item>

			<hr class="border-gray-50/30 dark:border-gray-800/30 my-1" />

			<DropdownMenu.Item
				class="flex gap-2 items-center px-3 py-1.5 text-sm  cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800 rounded-xl"
				on:click={() => {
					editHandler();
				}}
			>
				<Pencil />
				<div class="flex items-center">{$i18n.t('Edit')}</div>
			</DropdownMenu.Item>

			<DropdownMenu.Item
				class="flex gap-2 items-center px-3 py-1.5 text-sm  cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800 rounded-xl"
				on:click={() => {
					cloneHandler();
				}}
			>
				<DocumentDuplicate />

				<div class="flex items-center">{$i18n.t('Clone')}</div>
			</DropdownMenu.Item>

			<hr class="border-gray-50/30 dark:border-gray-800/30 my-1" />

			<DropdownMenu.Item
				class="flex gap-2 items-center px-3 py-1.5 text-sm  cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800 rounded-xl"
				on:click={() => {
					copyLinkHandler();
				}}
			>
				<Link />

				<div class="flex items-center">{$i18n.t('Copy Link')}</div>
			</DropdownMenu.Item>

			{#if $currentUser?.role === 'admin' || $currentUser?.permissions?.workspace?.apps_export}
				<DropdownMenu.Item
					class="flex gap-2 items-center px-3 py-1.5 text-sm  cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800 rounded-xl"
					on:click={() => {
						exportHandler();
					}}
				>
					<Download />

					<div class="flex items-center">{$i18n.t('Export')}</div>
				</DropdownMenu.Item>
			{/if}

			{#if $config?.features.enable_community_sharing}
				<DropdownMenu.Item
					class="flex gap-2 items-center px-3 py-1.5 text-sm  cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800  rounded-xl"
					on:click={() => {
						shareHandler();
					}}
				>
					<Share />
					<div class="flex items-center">{$i18n.t('Share')}</div>
				</DropdownMenu.Item>
			{/if}

			<hr class="border-gray-50/30 dark:border-gray-800/30 my-1" />

			<DropdownMenu.Item
				class="flex  gap-2  items-center px-3 py-1.5 text-sm  cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800 rounded-xl"
				on:click={() => {
					deleteHandler();
				}}
			>
				<GarbageBin />
				<div class="flex items-center">{$i18n.t('Delete')}</div>
			</DropdownMenu.Item>
		</DropdownMenu.Content>
	</div>
</Dropdown>
