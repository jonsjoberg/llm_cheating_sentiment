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
		What proportion (in %) of the reviews for each game, in the last 7 days on Steam, have mentioned
		cheating in a positive light (i.e. there are not many cheaters in the game, the developer is
		doing a good job to combat cheaters, etc) or a negative light (i.e. the game is overrun with
		cheaters, the developers is not doing enough, etc), or not mentioned cheating at all.
	</div>
	<div>
		<table>
			<thead>
				<tr>
					<td>Game</td>
					<td>Positive Reviews</td>
					<td>Negative Reviews</td>
					<td>Didn't mention cheating</td>
					<td>Total Reviews</td>
				</tr>
			</thead>
			<tbody>
				{#each data.appsWithReviews as a}
					<tr>
						<td>{a.app.name}</td>
						<td>{a.reviewsPerSentiment.positive}</td>
						<td>{a.reviewsPerSentiment.negative}</td>
						<td>{a.reviewsPerSentiment.notMentioned}</td>
						<td>
							{a.reviewsPerSentiment.positive +
								a.reviewsPerSentiment.negative +
								a.reviewsPerSentiment.notMentioned}
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>
</main>

<style>
	.bars {
		width: 1000px;
		padding: 10px;
	}
	main {
		width: 100%;
		display: flex;
		align-items: center;
		flex-direction: column;
		gap: 2em;
	}
	.explanation {
		width: 500px;
		text-align: center;
	}
	table {
		width: 100%;
	}
	table,
	tr,
	td {
		border: 1px dashed var(--main-color);
		border-collapse: collapse;
		padding: 0.25em 1em;
	}
	thead {
		font-weight: 700;
	}
</style>
