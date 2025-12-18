<script>
	import { toast } from 'svelte-sonner';
	import { goto } from '$app/navigation';

	import { onMount, getContext } from 'svelte';
	const i18n = getContext('i18n');

	import { page } from '$app/stores';

	import { getAppById, updateAppById } from '$lib/apis/apps';

	import AppEditor from '$lib/components/workspace/Apps/AppEditor.svelte';
	import { updateAppFromArtifactCode } from '$lib/stores';

	let app = null;

	onMount(async () => {
		const _id = $page.url.searchParams.get('id');
		if (_id) {
			app = await getAppById(localStorage.token, _id).catch((e) => {
				return null;
			});

			if ($updateAppFromArtifactCode?.sourceCode?.length > 0) {
				app.source_code = $updateAppFromArtifactCode.sourceCode;
				updateAppFromArtifactCode.set(null);
			}

			if (!app) {
				goto('/workspace/apps');
			}
		} else {
			goto('/workspace/apps');
		}
	});

	const onSubmit = async (appInfo) => {
		const res = await updateAppById(localStorage.token, appInfo.id, appInfo);

		if (res) {
			toast.success($i18n.t('App updated successfully'));
			await goto('/workspace/apps');
		}
	};
</script>

{#if app}
	<AppEditor edit={true} {app} {onSubmit} />
{/if}
