<script lang="ts">
	import Bar from '$lib/plot/Bar.svelte';
	import type { PageData } from './$types';

	let { data }: { data: PageData } = $props();
</script>

<main>
	<h1>Cheating sentiment</h1>
	<div class="bars">
		<Bar reviewData={data.appsWithReviews} />
	</div>
	<div class="explanation">
		Out of the reviews for this game in the last 2 weeks, what is proportion that had a negative vs
		positive view on cheating in this game
	</div>
</main>

<style>
	.bars {
		width: 500px;
		padding: 10px;
	}
	main {
		width: 100%;
		display: flex;
		align-items: center;
		flex-direction: column;
	}
	.explanation {
		width: 500px;
		text-align: center;
	}
</style>
