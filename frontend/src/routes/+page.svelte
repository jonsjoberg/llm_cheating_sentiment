<script lang="ts">
	import type { PageData } from './$types';

	let { data }: { data: PageData } = $props();
</script>

<h1>Welcome to SvelteKit</h1>
<p>Visit <a href="https://svelte.dev/docs/kit">svelte.dev/docs/kit</a> to read the documentation</p>
{#each data?.appsWithReviews as a}
	<p>{a.app.name} -{a.reviewsPerSentiment.negative} | + {a.reviewsPerSentiment.positive}</p>
{/each}
