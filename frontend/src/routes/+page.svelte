<script lang="ts">
	import OverTime from '$lib/OverTime.svelte';
	import Snapshot from '$lib/Snapshot.svelte';
	import type { PageData } from './$types';

	let { data }: { data: PageData } = $props();

	const appsWithReviews = $derived(data.appsWithReviews);
	const overtimeSentiment = $derived(data.overtimeSentiment);

	let active = $state('snapshot');
</script>

<main>
	<h1>cheating sentiment</h1>
	<div class="buttons">
		<button
			class={active === 'snapshot' ? 'active' : ''}
			onclick={() => {
				active = 'snapshot';
			}}>snapshot</button
		>
		<button
			class={active === 'overtime' ? 'active' : ''}
			onclick={() => {
				active = 'overtime';
			}}>over time</button
		>
	</div>
	<div class="info">
		{#if active === 'snapshot'}
			<Snapshot snapshotReviewData={appsWithReviews} />
		{:else}
			<OverTime {overtimeSentiment} />
		{/if}
	</div>
</main>

<style>
	main {
		width: 100%;
		display: flex;
		align-items: center;
		flex-direction: column;
		gap: 2em;
	}

	.buttons button {
		min-width: 200px;
	}

	.info {
		width: 1000px;
	}
</style>
