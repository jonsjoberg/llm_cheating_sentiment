<script lang="ts">
	import type { AppReviewsPerSentiment } from './firebase_server';
	import Bar from './plot/Bar.svelte';
	import Table from './Table.svelte';

	const { snapshotReviewData }: { snapshotReviewData: AppReviewsPerSentiment[] } = $props();
</script>

<div class="snapshot">
	<Bar reviewData={snapshotReviewData} />

	<div class="explanation">
		What proportion (in %) of the reviews for each game, in the last 7 days on Steam, have mentioned
		cheating in a positive light (i.e. there are not many cheaters in the game, the developer is
		doing a good job to combat cheaters, etc) or a negative light (i.e. the game is overrun with
		cheaters, the developers is not doing enough, etc), or not mentioned cheating at all.
	</div>
	<div>
		<Table {snapshotReviewData} />
	</div>
</div>

<style>
	.snapshot {
		width: 100%;
		display: flex;
		align-items: center;
		flex-direction: column;
		gap: 2em;
	}
</style>
