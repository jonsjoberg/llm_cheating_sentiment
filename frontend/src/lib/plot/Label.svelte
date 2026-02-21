<script lang="ts">
	import { fade } from 'svelte/transition';

	let { text } = $props();

	let textElement = $state();

	let box = $state({ x: 0, y: 0, width: 0, height: 0 });

	const padding = 5;

	$effect(() => {
		const textBBox = textElement.getBBox();
		box = {
			x: textBBox.x - padding,
			y: textBBox.y - padding / 2,
			width: textBBox.width + padding * 2,
			height: textBBox.height + padding
		};
	});
</script>

<g transition:fade>
	<rect class="labelBackground" x={box.x} y={box.y} width={box.width} height={box.height} />
	<text bind:this={textElement}>
		{text}
	</text>
</g>

<style>
	.labelBackground {
		fill: var(--background-selected);
		stroke: var(--main-color);
		stroke-width: 1px;
	}
</style>
