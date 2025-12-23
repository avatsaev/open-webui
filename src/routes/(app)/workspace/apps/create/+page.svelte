<script lang="ts">
	import { toast } from 'svelte-sonner';
	import { goto } from '$app/navigation';
	import { createAppFromArtifactCode } from '$lib/stores';

	import { onMount, getContext } from 'svelte';
	import { createNewApp } from '$lib/apis/apps';

	import AppEditor from '$lib/components/workspace/Apps/AppEditor.svelte';

	const i18n = getContext('i18n');
	let sourceCode = '';
	let sourceChatId: string | null = null;

	const onSubmit = async (appInfo) => {
		if (appInfo) {
			const res = await createNewApp(localStorage.token, {
				...appInfo,
				meta: {
					...appInfo.meta,
					icon_image_url: appInfo.meta.icon_image_url ?? '/static/favicon.png',
					thumbnail_image_url: appInfo.meta.thumbnail_image_url ?? '/static/favicon.png'
				},
				params: { ...appInfo.params }
			}).catch((error) => {
				toast.error(`${error}`);
				return null;
			});

			if (res) {
				toast.success($i18n.t('App created successfully!'));
				await goto('/workspace/apps');
			}
		}
	};

	let app = null;

	onMount(async () => {
		if ($createAppFromArtifactCode) {
			sourceCode = $createAppFromArtifactCode.sourceCode;
			sourceChatId = $createAppFromArtifactCode.sourceChatId;
		}
		createAppFromArtifactCode.set(null);

		window.addEventListener('message', async (event) => {
			if (
				!['https://openwebui.com', 'https://www.openwebui.com', 'http://localhost:5173'].includes(
					event.origin
				)
			) {
				return;
			}

			try {
				let data = JSON.parse(event.data);

				if (data?.info) {
					data = data.info;
				}

				app = data;
			} catch (e) {
				console.error('Failed to parse message data:', e);
			}
		});

		if (window.opener ?? false) {
			window.opener.postMessage('loaded', '*');
		}

		if (sessionStorage.app) {
			app = JSON.parse(sessionStorage.app);
			sessionStorage.removeItem('app');
		}
	});
</script>

{#key app}
	<AppEditor {app} source_code={sourceCode} source_chat_id={sourceChatId} {onSubmit} />
{/key}
