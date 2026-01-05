<script lang="ts">
	import { getContext } from 'svelte';
	import { goto } from '$app/navigation';

	import { getAppIconImageUrl } from '$lib/apis/apps';
	import Tooltip from '$lib/components/common/Tooltip.svelte';

	const i18n = getContext('i18n');

	export let app: any;
</script>

<!-- svelte-ignore a11y_no_static_element_interactions -->
<!-- svelte-ignore a11y_click_events_have_key_events -->
<div
	class="flex flex-col cursor-pointer bg-gray-50 dark:bg-gray-850 hover:bg-gray-100 dark:hover:bg-gray-800 transition-all duration-200 rounded-2xl w-full p-4 border border-gray-200 dark:border-gray-700 hover:shadow-md"
	on:click={() => {
		goto(`/apps/${encodeURIComponent(app.id)}`);
	}}
>
	<div class="flex items-center gap-3 mb-2">
		<div class="shrink-0">
			<img
				src={getAppIconImageUrl(app.id)}
				alt={app.title}
				class="rounded-xl size-14 object-cover shadow-sm"
			/>
		</div>

		<Tooltip content={app.title} className="w-fit flex-1 min-w-0" placement="top-start">
			<div class="font-semibold line-clamp-1 capitalize text-sm">
				{app.title}
			</div>
		</Tooltip>
	</div>

	{#if (app?.meta?.description ?? '').trim()}
		<div class="text-xs text-gray-600 dark:text-gray-400 line-clamp-2 leading-relaxed">
			{app.meta.description}
		</div>
	{/if}
</div>
