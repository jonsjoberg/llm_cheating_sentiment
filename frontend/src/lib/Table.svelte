<script lang="ts">
	let { snapshotReviewData } = $props();
</script>

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
		{#each snapshotReviewData as a}
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

<style>
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
