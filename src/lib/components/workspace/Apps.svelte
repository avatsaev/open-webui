<script lang="ts">
	import { marked } from 'marked';

	import { toast } from 'svelte-sonner';

	import fileSaver from 'file-saver';
	const { saveAs } = fileSaver;

	import { onMount, getContext, tick } from 'svelte';
	import { goto } from '$app/navigation';
	const i18n = getContext('i18n');

	import { WEBUI_NAME, config, mobile, user } from '$lib/stores';
	import {
		createNewApp,
		deleteAppById,
		getAppItems as getWorkspaceApps,
		getAppTags,
		getAppIconImageUrl,
		toggleAppById,
		updateAppById,
		importApps,
		exportApps
	} from '$lib/apis/apps';

	import { getGroups } from '$lib/apis/groups';

	import { capitalizeFirstLetter, copyToClipboard } from '$lib/utils';

	import EllipsisHorizontal from '../icons/EllipsisHorizontal.svelte';
	import AppMenu from './Apps/AppMenu.svelte';
	import AppDeleteConfirmDialog from '../common/ConfirmDialog.svelte';
	import Tooltip from '../common/Tooltip.svelte';
	import GarbageBin from '../icons/GarbageBin.svelte';
	import Search from '../icons/Search.svelte';
	import Plus from '../icons/Plus.svelte';
	import Switch from '../common/Switch.svelte';
	import Spinner from '../common/Spinner.svelte';
	import XMark from '../icons/XMark.svelte';
	import ViewSelector from './common/ViewSelector.svelte';
	import TagSelector from './common/TagSelector.svelte';
	import Pagination from '../common/Pagination.svelte';

	let shiftKey = false;

	let importFiles;
	let appsImportInputElement: HTMLInputElement;
	let tagsContainerElement: HTMLDivElement;

	let loaded = false;

	let showAppDeleteConfirm = false;

	let selectedApp = null;

	let groupIds = [];

	let tags = [];
	let selectedTag = '';

	let query = '';
	let viewOption = '';

	let page = 1;
	let apps = null;
	let total = null;

	$: if (
		page !== undefined &&
		query !== undefined &&
		selectedTag !== undefined &&
		viewOption !== undefined
	) {
		getAppList();
	}

	const getAppList = async () => {
		try {
			const res = await getWorkspaceApps(
				localStorage.token,
				query,
				viewOption,
				selectedTag,
				null,
				null,
				page
			).catch((error) => {
				toast.error(`${error}`);
				return null;
			});

			if (res) {
				apps = res.items;
				total = res.total;

				// get tags
				tags = await getAppTags(localStorage.token).catch((error) => {
					toast.error(`${error}`);
					return [];
				});
			}
		} catch (err) {
			console.error(err);
		}
	};

	const deleteAppHandler = async (app) => {
		const res = await deleteAppById(localStorage.token, app.id).catch((e) => {
			toast.error(`${e}`);
			return null;
		});

		if (res) {
			toast.success($i18n.t(`Deleted {{name}}`, { name: app.title }));

			page = 1;
			getAppList();
		}
	};

	const cloneAppHandler = async (app) => {
		sessionStorage.app = JSON.stringify({
			...app,
			id: `${app.id}-clone`,
			title: `${app.title} (Clone)`
		});
		goto('/workspace/apps/create');
	};

	const shareAppHandler = async (app) => {
		toast.success($i18n.t('Redirecting you to Open WebUI Community'));

		const url = 'https://openwebui.com';

		const tab = await window.open(`${url}/apps/create`, '_blank');

		const messageHandler = (event) => {
			if (event.origin !== url) return;
			if (event.data === 'loaded') {
				tab.postMessage(JSON.stringify(app), '*');
				window.removeEventListener('message', messageHandler);
			}
		};

		window.addEventListener('message', messageHandler, false);
	};

	const copyLinkHandler = async (app) => {
		const baseUrl = window.location.origin;
		const res = await copyToClipboard(`${baseUrl}/?app=${encodeURIComponent(app.id)}`);

		if (res) {
			toast.success($i18n.t('Copied link to clipboard'));
		} else {
			toast.error($i18n.t('Failed to copy link'));
		}
	};

	const downloadApps = async (apps) => {
		let blob = new Blob([JSON.stringify(apps)], {
			type: 'application/json'
		});
		saveAs(blob, `apps-export-${Date.now()}.json`);
	};

	const exportAppHandler = async (app) => {
		let blob = new Blob([JSON.stringify([app])], {
			type: 'application/json'
		});
		saveAs(blob, `${app.id}-${Date.now()}.json`);
	};

	onMount(async () => {
		viewOption = localStorage.workspaceAppsViewOption ?? '';
		page = 1;

		let groups = await getGroups(localStorage.token);
		groupIds = groups.map((group) => group.id);

		loaded = true;

		const onKeyDown = (event) => {
			if (event.key === 'Shift') {
				shiftKey = true;
			}
		};

		const onKeyUp = (event) => {
			if (event.key === 'Shift') {
				shiftKey = false;
			}
		};

		const onBlur = () => {
			shiftKey = false;
		};

		window.addEventListener('keydown', onKeyDown);
		window.addEventListener('keyup', onKeyUp);
		window.addEventListener('blur', onBlur);

		return () => {
			window.removeEventListener('keydown', onKeyDown);
			window.removeEventListener('keyup', onKeyUp);
			window.removeEventListener('blur', onBlur);
		};
	});
</script>

<svelte:head>
	<title>
		{$i18n.t('Apps')} • {$WEBUI_NAME}
	</title>
</svelte:head>

{#if loaded}
	<AppDeleteConfirmDialog
		bind:show={showAppDeleteConfirm}
		on:confirm={() => {
			deleteAppHandler(selectedApp);
		}}
	/>

	<div class="flex flex-col gap-1 px-1 mt-1.5 mb-3">
		<input
			id="apps-import-input"
			bind:this={appsImportInputElement}
			bind:files={importFiles}
			type="file"
			accept=".json"
			hidden
			on:change={() => {
				console.log(importFiles);

				let reader = new FileReader();
				reader.onload = async (event) => {
					let savedApps = [];
					try {
						savedApps = JSON.parse(event.target.result);
						console.log(savedApps);
					} catch (e) {
						toast.error($i18n.t('Invalid JSON file'));
						return;
					}

					const res = await importApps(localStorage.token, savedApps).catch((error) => {
						toast.error(`${error}`);
						return null;
					});

					if (res) {
						toast.success($i18n.t('Apps imported successfully'));
						page = 1;
						getAppList();
					}
				};

				reader.readAsText(importFiles[0]);
			}}
		/>
		<div class="flex justify-between items-center">
			<div class="flex items-center md:self-center text-xl font-medium px-0.5 gap-2 shrink-0">
				<div>
					{$i18n.t('Apps')}
				</div>

				<div class="text-lg font-medium text-gray-500 dark:text-gray-500">
					{total}
				</div>
			</div>

			<div class="flex w-full justify-end gap-1.5">
				{#if $user?.role === 'admin' || $user?.permissions?.workspace?.apps_import}
					<button
						class="flex text-xs items-center space-x-1 px-3 py-1.5 rounded-xl bg-gray-50 hover:bg-gray-100 dark:bg-gray-850 dark:hover:bg-gray-800 dark:text-gray-200 transition"
						on:click={() => {
							appsImportInputElement.click();
						}}
					>
						<div class=" self-center font-medium line-clamp-1">
							{$i18n.t('Import')}
						</div>
					</button>
				{/if}

				{#if total && ($user?.role === 'admin' || $user?.permissions?.workspace?.apps_export)}
					<button
						class="flex text-xs items-center space-x-1 px-3 py-1.5 rounded-xl bg-gray-50 hover:bg-gray-100 dark:bg-gray-850 dark:hover:bg-gray-800 dark:text-gray-200 transition"
						on:click={async () => {
							const allApps = await exportApps(localStorage.token);
							downloadApps(allApps);
						}}
					>
						<div class=" self-center font-medium line-clamp-1">
							{$i18n.t('Export')}
						</div>
					</button>
				{/if}
				<a
					class=" px-2 py-1.5 rounded-xl bg-black text-white dark:bg-white dark:text-black transition font-medium text-sm flex items-center"
					href="/workspace/apps/create"
				>
					<Plus className="size-3" strokeWidth="2.5" />

					<div class=" hidden md:block md:ml-1 text-xs">{$i18n.t('New App')}</div>
				</a>
			</div>
		</div>
	</div>

	<div
		class="py-2 bg-white dark:bg-gray-900 rounded-3xl border border-gray-100/30 dark:border-gray-850/30"
	>
		<div class="px-3.5 flex flex-1 items-center w-full space-x-2 py-0.5 pb-2">
			<div class="flex flex-1 items-center">
				<div class=" self-center ml-1 mr-3">
					<Search className="size-3.5" />
				</div>
				<input
					class=" w-full text-sm py-1 rounded-r-xl outline-hidden bg-transparent"
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

		<div
			class="px-3 flex w-full bg-transparent overflow-x-auto scrollbar-none"
			on:wheel={(e) => {
				if (e.deltaY !== 0) {
					e.preventDefault();
					e.currentTarget.scrollLeft += e.deltaY;
				}
			}}
		>
			<div
				class="flex gap-0.5 w-fit text-center text-sm rounded-full bg-transparent px-0.5 whitespace-nowrap"
				bind:this={tagsContainerElement}
			>
				<ViewSelector
					bind:value={viewOption}
					onChange={async (value) => {
						localStorage.workspaceAppsViewOption = value;
						await tick();
					}}
				/>

				{#if (tags ?? []).length > 0}
					<TagSelector
						bind:value={selectedTag}
						items={tags.map((tag) => {
							return { value: tag, label: tag };
						})}
					/>
				{/if}
			</div>
		</div>

		{#if (apps ?? []).length !== 0}
			<div class=" px-3 my-2 gap-1 lg:gap-2 grid lg:grid-cols-2" id="app-list">
				{#each apps as app (app.id)}
					<!-- svelte-ignore a11y_no_static_element_interactions -->
					<!-- svelte-ignore a11y_click_events_have_key_events -->
					<div
						class="  flex cursor-pointer dark:hover:bg-gray-850/50 hover:bg-gray-50 transition rounded-2xl w-full p-2.5"
						id="app-item-{app.id}"
						on:click={() => {
							if (
								$user?.role === 'admin' ||
								app.user_id === $user?.id ||
								(app.access_control?.write?.group_ids ?? []).some((wg) => groupIds.includes(wg))
							) {
								goto(`/workspace/apps/edit?id=${encodeURIComponent(app.id)}`);
							}
						}}
					>
						<div class="flex group/item gap-3.5 w-full">
							<div class="self-center pl-0.5">
								<div class="flex bg-white rounded-2xl">
									<div
										class="{app.is_active
											? ''
											: 'opacity-50 dark:opacity-50'} bg-transparent rounded-2xl"
									>
										<img
											src={getAppIconImageUrl(app.id)}
											alt="app icon"
											class=" rounded-2xl size-12 object-cover"
										/>
									</div>
								</div>
							</div>

							<div class=" shrink-0 flex w-full min-w-0 flex-1 pr-1 self-center">
								<div class="flex h-full w-full flex-1 flex-col justify-start self-center group">
									<div class="flex-1 w-full">
										<div class="flex items-center justify-between w-full">
											<Tooltip content={app.title} className=" w-fit" placement="top-start">
												<div class=" font-medium line-clamp-1 capitalize">
													{app.title}
												</div>
											</Tooltip>

											<div class=" flex items-center gap-1">
												<div class="flex justify-end w-full {app.is_active ? '' : 'text-gray-500'}">
													<div class="flex justify-between items-center w-full">
														<div class=""></div>
														<div class="flex flex-row gap-0.5 items-center">
															{#if shiftKey}
																<Tooltip content={$i18n.t('Delete')}>
																	<button
																		class="self-center w-fit text-sm p-1.5 dark:text-white hover:bg-black/5 dark:hover:bg-white/5 rounded-xl"
																		type="button"
																		on:click={(e) => {
																			e.stopPropagation();
																			deleteAppHandler(app);
																		}}
																	>
																		<GarbageBin />
																	</button>
																</Tooltip>
															{:else}
																<AppMenu
																	user={$user}
																	{app}
																	editHandler={() => {
																		goto(`/workspace/apps/edit?id=${encodeURIComponent(app.id)}`);
																	}}
																	shareHandler={() => {
																		shareAppHandler(app);
																	}}
																	cloneHandler={() => {
																		cloneAppHandler(app);
																	}}
																	exportHandler={() => {
																		exportAppHandler(app);
																	}}
																	copyLinkHandler={() => {
																		copyLinkHandler(app);
																	}}
																	deleteHandler={() => {
																		selectedApp = app;
																		showAppDeleteConfirm = true;
																	}}
																	onClose={() => {}}
																>
																	<div
																		class="self-center w-fit p-1 text-sm dark:text-white hover:bg-black/5 dark:hover:bg-white/5 rounded-xl"
																	>
																		<EllipsisHorizontal className="size-5" />
																	</div>
																</AppMenu>
															{/if}
														</div>
													</div>
												</div>

												<button
													on:click={(e) => {
														e.stopPropagation();
													}}
												>
													<Tooltip
														content={app.is_active ? $i18n.t('Enabled') : $i18n.t('Disabled')}
													>
														<Switch
															bind:state={app.is_active}
															on:change={async () => {
																await toggleAppById(localStorage.token, app.id);
																getAppList();
															}}
														/>
													</Tooltip>
												</button>
											</div>
										</div>

										<div class=" flex gap-1 pr-2 -mt-1 items-center">
											<Tooltip
												content={app?.user?.email ?? $i18n.t('Deleted User')}
												className="flex shrink-0"
												placement="top-start"
											>
												<div class="shrink-0 text-gray-500 text-xs">
													{$i18n.t('By {{name}}', {
														name: capitalizeFirstLetter(
															app?.user?.name ?? app?.user?.email ?? $i18n.t('Deleted User')
														)
													})}
												</div>
											</Tooltip>

											<div>·</div>

											<Tooltip
												content={marked.parse(app?.meta?.description ?? app.id)}
												className=" w-fit text-left"
												placement="top-start"
											>
												<div class="flex gap-1 text-xs overflow-hidden">
													<div class="line-clamp-1">
														{#if (app?.meta?.description ?? '').trim()}
															{app?.meta?.description}
														{:else}
															{app.id}
														{/if}
													</div>
												</div>
											</Tooltip>
										</div>
									</div>
								</div>
							</div>
						</div>
					</div>
				{/each}
			</div>

			{#if total > 30}
				<Pagination bind:page count={total} perPage={30} />
			{/if}
		{:else}
			<div class=" w-full h-full flex flex-col justify-center items-center my-16 mb-24">
				<div class="max-w-md text-center">
					<div class=" text-3xl mb-3">😕</div>
					<div class=" text-lg font-medium mb-1">{$i18n.t('No apps found')}</div>
					<div class=" text-gray-500 text-center text-xs">
						{$i18n.t('Try adjusting your search or filter to find what you are looking for.')}
					</div>
				</div>
			</div>
		{/if}
	</div>
{:else}
	<div class="w-full h-full flex justify-center items-center">
		<Spinner className="size-5" />
	</div>
{/if}
