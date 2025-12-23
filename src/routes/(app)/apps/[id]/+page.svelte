<script lang="ts">
	import { page } from '$app/stores';

	import App from '$lib/components/apps/App.svelte';
</script>

<App id={$page.params.id} />
