<script lang="ts">
	import { toast } from 'svelte-sonner';
	import { goto } from '$app/navigation';

	import { onMount, getContext } from 'svelte';
	import { user } from '$lib/stores';

	import Tags from '$lib/components/common/Tags.svelte';
	import Textarea from '$lib/components/common/Textarea.svelte';
	import CodeEditor from '$lib/components/common/CodeEditor.svelte';
	import AccessControl from '../common/AccessControl.svelte';
	import Spinner from '$lib/components/common/Spinner.svelte';

	const i18n = getContext('i18n');

	export let onSubmit: Function;
	export let app = null;
	export let edit = false;

	let loading = false;

	let filesInputElement;
	let inputFiles;

	let loaded = false;

	// ///////////
	// app fields
	// ///////////

	let title = '';
	export let source_code = '';
	let _source_code = ''; // Temporary variable for CodeEditor onChange
	export let source_chat_id = '';

	let info = {
		id: '',
		title: '',
		source_code: '',
		source_chat_id: null,
		meta: {
			icon_image_url: '/static/favicon.png',
			thumbnail_image_url: '/static/favicon.png',
			description: '',
			tags: []
		},
		params: {},
		access_control: {},
		is_active: true
	};

	let accessControl = {};

	const submitHandler = async () => {
		loading = true;

		info.title = title;
		info.source_code = source_code;
		info.source_chat_id = source_chat_id || null;

		if (title === '') {
			toast.error($i18n.t('App title is required.'));
			loading = false;
			return;
		}

		if (source_code === '') {
			toast.error($i18n.t('Source code is required.'));
			loading = false;
			return;
		}

		info.access_control = accessControl;

		info.meta.description = info.meta.description.trim() === '' ? null : info.meta.description;

		// Transform tags from [{name: string}] to [string] for backend
		if (info.meta.tags && Array.isArray(info.meta.tags)) {
			info.meta.tags = info.meta.tags.map((tag) => (typeof tag === 'string' ? tag : tag.name));
		}

		await onSubmit(info);

		loading = false;
	};

	onMount(async () => {
		if (app) {
			title = app.title;
			source_code = app.source_code;
			source_chat_id = app.source_chat_id ?? '';

			info = {
				...app,
				meta: {
					icon_image_url: app.meta?.icon_image_url ?? '/static/favicon.png',
					thumbnail_image_url: app.meta?.thumbnail_image_url ?? '/static/favicon.png',
					description: app.meta?.description ?? '',
					// Transform tags from [string] to [{name: string}] for Tags component
					tags: (app.meta?.tags ?? []).map((tag) => (typeof tag === 'string' ? { name: tag } : tag))
				},
				params: app.params ?? {},
				access_control: app.access_control ?? {}
			};

			if ('access_control' in app) {
				accessControl = app.access_control;
			} else {
				accessControl = {};
			}
		}

		loaded = true;
	});
</script>

{#if loaded}
	<div class="w-full max-h-full flex justify-center">
		<input
			id="files-input"
			bind:this={filesInputElement}
			bind:files={inputFiles}
			type="file"
			hidden
			accept="image/*"
			on:change={() => {
				let reader = new FileReader();
				reader.onload = (event) => {
					let originalImageUrl = `${event.target.result}`;

					const img = new Image();
					img.src = originalImageUrl;

					img.onload = function () {
						const canvas = document.createElement('canvas');
						const ctx = canvas.getContext('2d');

						// Calculate the aspect ratio of the image
						const aspectRatio = img.width / img.height;

						// Calculate the new width and height to fit within 250x250
						let newWidth, newHeight;
						if (aspectRatio > 1) {
							newWidth = 250 * aspectRatio;
							newHeight = 250;
						} else {
							newWidth = 250;
							newHeight = 250 / aspectRatio;
						}

						// Set the canvas size
						canvas.width = 250;
						canvas.height = 250;

						// Calculate the position to center the image
						const offsetX = (250 - newWidth) / 2;
						const offsetY = (250 - newHeight) / 2;

						// Draw the image on the canvas
						ctx.drawImage(img, offsetX, offsetY, newWidth, newHeight);

						// Get the base64 representation of the compressed image
						const compressedSrc = canvas.toDataURL();

						// Display the compressed image
						info.meta.icon_image_url = compressedSrc;

						inputFiles = null;
						filesInputElement.value = '';
					};
				};

				if (
					inputFiles &&
					inputFiles.length > 0 &&
					['image/gif', 'image/webp', 'image/jpeg', 'image/png', 'image/svg+xml'].includes(
						inputFiles[0]['type']
					)
				) {
					reader.readAsDataURL(inputFiles[0]);
				} else {
					console.log(`Unsupported File Type '${inputFiles[0]['type']}'.`);
					inputFiles = null;
				}
			}}
		/>

		<form
			class="w-full max-w-6xl px-2 md:px-0 my-10"
			on:submit={(e) => {
				e.preventDefault();
				submitHandler();
			}}
		>
			<div class="flex flex-col md:flex-row justify-between gap-6">
				<div class="self-center md:self-start flex justify-center my-2 shrink-0">
					<div class="self-center">
						<button
							class="rounded-xl flex shrink-0 items-center bg-white shadow-xl group relative"
							type="button"
							on:click={() => {
								filesInputElement.click();
							}}
						>
							{#if info.meta.icon_image_url}
								<img
									src={info.meta.icon_image_url}
									alt="app icon"
									class="rounded-xl sm:size-60 size-max object-cover shrink-0"
								/>
							{:else}
								<img
									src="/static/favicon.png"
									alt="app icon"
									class="rounded-xl sm:size-60 size-max object-cover shrink-0"
								/>
							{/if}

							<div class="absolute bottom-0 right-0 z-10">
								<div class="m-1.5">
									<div
										class="shadow-xl p-1 rounded-full border-2 border-white bg-gray-800 text-white group-hover:bg-gray-600 transition dark:border-black dark:bg-white dark:group-hover:bg-gray-200 dark:text-black"
									>
										<svg
											xmlns="http://www.w3.org/2000/svg"
											viewBox="0 0 16 16"
											fill="currentColor"
											class="size-5"
										>
											<path
												fill-rule="evenodd"
												d="M2 4a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V4Zm10.5 5.707a.5.5 0 0 0-.146-.353l-1-1a.5.5 0 0 0-.708 0L9.354 9.646a.5.5 0 0 1-.708 0L6.354 7.354a.5.5 0 0 0-.708 0l-2 2a.5.5 0 0 0-.146.353V12a.5.5 0 0 0 .5.5h8a.5.5 0 0 0 .5-.5V9.707ZM12 5a1 1 0 1 1-2 0 1 1 0 0 1 2 0Z"
												clip-rule="evenodd"
											/>
										</svg>
									</div>
								</div>
							</div>

							<div
								class="absolute top-0 bottom-0 left-0 right-0 bg-white dark:bg-black rounded-lg opacity-0 group-hover:opacity-20 transition"
							/>
						</button>

						<div class="flex w-full mt-1 justify-end">
							<button
								class="px-2 py-1 text-gray-500 rounded-lg text-xs"
								on:click={() => {
									info.meta.icon_image_url = '/static/favicon.png';
								}}
								type="button"
							>
								{$i18n.t('Reset Image')}
							</button>
						</div>
					</div>
				</div>

				<div class="w-full">
					<div class="flex flex-col">
						<div class="flex justify-between items-start my-2">
							<div class="flex flex-col w-full">
								<div class="flex-1 w-full">
									<input
										class="text-4xl font-medium w-full bg-transparent outline-hidden"
										placeholder={$i18n.t('App Title')}
										bind:value={title}
										required
									/>
								</div>
							</div>
						</div>
						<div class="my-1">
							<Textarea
								className="text-sm w-full bg-transparent outline-hidden resize-none overflow-y-hidden"
								placeholder={$i18n.t('Add a short description about what this app does')}
								bind:value={info.meta.description}
							/>
						</div>

						<div class="w-full mb-1 max-w-full">
							<div>
								<Tags
									tags={info?.meta?.tags ?? []}
									on:delete={(e) => {
										const tagName = e.detail;
										info.meta.tags = info.meta.tags.filter((tag) => tag.name !== tagName);
									}}
									on:add={(e) => {
										const tagName = e.detail;
										if (!(info?.meta?.tags ?? null)) {
											info.meta.tags = [{ name: tagName }];
										} else {
											info.meta.tags = [...info.meta.tags, { name: tagName }];
										}
									}}
								/>
							</div>
						</div>
					</div>

					<hr class="border-gray-100/30 dark:border-gray-850/30 my-2" />

					<div class="my-2">
						<div class="flex w-full justify-between mb-2">
							<div class="self-center text-xs font-medium text-gray-500">
								{$i18n.t('Source Code')}
							</div>
						</div>

						<div class="overflow-auto h-64 rounded-lg max-w-full">
							<CodeEditor
								value={source_code}
								lang="javascript"
								onChange={(e) => {
									_source_code = e;
									source_code = e;
								}}
								onSave={() => {
									// CodeEditor save handler - could submit form if needed
								}}
							/>
						</div>

						<div class="hidden">
							<input
								class="w-full rounded-lg py-2 px-4 text-sm bg-gray-50 dark:text-gray-300 dark:bg-gray-850 outline-none"
								type="text"
								placeholder={$i18n.t('Chat ID this app was created from')}
								bind:value={source_chat_id}
								autocomplete="off"
							/>
						</div>
					</div>

					<hr class="border-gray-100/30 dark:border-gray-850/30 my-2" />

					<div class="my-2">
						<div class="text-xs font-medium text-gray-500 mb-3">
							{$i18n.t('Access Control')}
						</div>
						<AccessControl
							bind:accessControl
							onChange={(ac) => {
								accessControl = ac;
							}}
							accessRoles={['read', 'write']}
							share={$user?.permissions?.sharing?.apps || $user?.role === 'admin'}
							sharePublic={$user?.permissions?.sharing?.public_apps || $user?.role === 'admin'}
						/>
					</div>

					<hr class="border-gray-100/30 dark:border-gray-850/30 my-2" />

					<div class="my-2 flex justify-end gap-2">
						<button
							class="px-4 py-2.5 text-sm font-medium bg-gray-100 hover:bg-gray-200 dark:bg-gray-800 dark:hover:bg-gray-700 text-gray-800 dark:text-gray-100 transition rounded-lg"
							type="button"
							on:click={() => goto('/workspace/apps')}
						>
							{$i18n.t('Cancel')}
						</button>

						{#if loading}
							<button
								class="px-4 py-2.5 text-sm font-medium bg-black hover:bg-gray-900 text-white dark:bg-white dark:text-black dark:hover:bg-gray-100 transition rounded-lg flex flex-row space-x-1 items-center cursor-not-allowed"
								disabled={loading}
							>
								<Spinner className="size-4" />
								<div class="ml-2 self-center font-medium">
									{$i18n.t('Saving...')}
								</div>
							</button>
						{:else}
							<button
								class="px-4 py-2.5 text-sm font-medium bg-black hover:bg-gray-900 text-white dark:bg-white dark:text-black dark:hover:bg-gray-100 transition rounded-lg"
								type="submit"
							>
								{edit ? $i18n.t('Update App') : $i18n.t('Create App')}
							</button>
						{/if}
					</div>
				</div>
			</div>
		</form>
	</div>
{:else}
	<div class="w-full h-full flex justify-center items-center">
		<Spinner className="size-5" />
	</div>
{/if}
