<script lang="ts">
	import type { SentimentPerDaysAndApp } from '$lib/firebase_server';
	import Line from './plot/Line.svelte';

	const { overtimeSentiment }: { overtimeSentiment: SentimentPerDaysAndApp[] } = $props();
</script>

<div class="overTime">
	<h3>Under Construction</h3>
	<Line {overtimeSentiment} />
</div>
