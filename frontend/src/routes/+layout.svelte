<script lang="ts">
	import './layout.css';
	import favicon from './favicon.png';
	let { children } = $props();
</script>

<svelte:head>
	<!-- <link rel="preconnect" href="https://fonts.googleapis.com" />
	<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
	<link
		href="https://fonts.googleapis.com/css2?family=Doto:wght@100..900&display=swap"
		rel="stylesheet"
	/> -->
	<link rel="preconnect" href="https://fonts.googleapis.com" />
	<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
	<link
		href="https://fonts.googleapis.com/css2?family=Silkscreen:wght@400;700&display=swap"
		rel="stylesheet"
	/>
	<link rel="icon" href={favicon} />
	<title>What's the sentiment around cheating in your game?</title>
</svelte:head>
{@render children()}
