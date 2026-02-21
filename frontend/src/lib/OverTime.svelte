<script lang="ts">
	import type { SentimentPerDaysAndApp } from '$lib/firebase_server';
	import Line from './plot/Line.svelte';

	const { overtimeSentiment }: { overtimeSentiment: SentimentPerDaysAndApp[] } = $props();
</script>

<div class="overTime">
	<Line {overtimeSentiment} />
</div>
