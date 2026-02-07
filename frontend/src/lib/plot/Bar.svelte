<script lang="ts">
	import type { AppReviewsPerSentiment } from '$lib/firebase_server';
	import { scaleLinear } from 'd3-scale';

	const { reviewData }: { reviewData: AppReviewsPerSentiment[] } = $props();
	const plotData = $derived(
		reviewData.map((r) => {
			return {
				name: r.app.name,
				positivePct:
					(100 * r.reviewsPerSentiment.positive) /
					(r.reviewsPerSentiment.positive +
						r.reviewsPerSentiment.notMentioned +
						r.reviewsPerSentiment.negative),
				negativePct:
					(-100 * r.reviewsPerSentiment.negative) /
					(r.reviewsPerSentiment.positive +
						r.reviewsPerSentiment.notMentioned +
						r.reviewsPerSentiment.negative)
			};
		})
	);

	const calculateXTicks = (maxPct: number, spacing: number): number[] => {
		const limit = (Math.floor(maxPct / spacing) + 1) * spacing;
		const xTicks = Array.from(
			{ length: (limit * 2) / spacing + 1 },
			(_, i) => -limit + i * spacing
		);
		return xTicks;
	};

	const maxPositivePct = $derived(Math.max(...plotData.map((i) => i.positivePct!)));
	const minNegativePct = $derived(Math.min(...plotData.map((i) => i.negativePct!)));
	const maxPct = $derived(Math.max(maxPositivePct, -minNegativePct));
	// const spacing = $derived(maxPct > 10 ? 5 : 1);
	const spacing = 25;
	const xTicks = $derived(calculateXTicks(maxPct, spacing));
	const padding = 20;

	let width = $state(500);
	const height = $derived(50 * plotData.length + padding);
	const innerHeight = $derived(height - 3 * padding);
	const barheight = $derived((innerHeight / plotData.length) * 0.9);

	const xScale = $derived(
		scaleLinear()
			.domain([-100, 100])
			.range([padding, width - padding])
	);

	const zeroX = $derived(xScale(0));

	const yScale = $derived(
		scaleLinear()
			.domain([0, plotData.length])
			.range([padding / 2, height - 2 * padding])
	);
</script>

<div class="chart" bind:clientWidth={width}>
	<svg {width} {height}>
		<g>
			{#each xTicks as tick}
				<g transform="translate({xScale(tick)}, 0)" class="tick">
					<line y1="0" y2={height - 2 * padding} />
					<text y={height - padding} text-anchor="middle">{tick}</text>
				</g>
			{/each}
		</g>

		<g class="positiveBar">
			{#each plotData as d, i}
				<rect x={zeroX} y={yScale(i)} width={xScale(d.positivePct) - zeroX} height={barheight} />
			{/each}
		</g>
		<g class="negativeBar">
			{#each plotData as d, i}
				<rect
					x={xScale(d.negativePct)}
					y={yScale(i)}
					width={zeroX - xScale(d.negativePct)}
					height={barheight}
				/>
			{/each}
		</g>
		<g class="name">
			{#each plotData as d, i}
				<text
					y={yScale(i) + barheight / 2}
					x={zeroX}
					text-anchor="middle"
					dominant-baseline="middle">{d.name}</text
				>
			{/each}
		</g>
		<g class="sentiments">
			<text y={height} x={xScale(50)} text-anchor="middle">Positive</text>
			<text y={height} x={xScale(-50)} text-anchor="middle">Negative</text>
		</g>
	</svg>
</div>

<style>
	.positiveBar rect {
		fill: var(--positive-color);
		stroke: none;
	}
	.negativeBar rect {
		fill: var(--negative-color);
		stroke: none;
	}
	.tick line {
		stroke: var(--main-color);
		stroke-dasharray: 2;
		opacity: 0.5;
	}
	.tick text {
		fill: var(--main-color);
	}
	.name text {
		fill: var(--main-color);
		filter: drop-shadow(2px 2px 0px #282c34);
	}
	.sentiments text {
		fill: var(--main-color);
	}
</style>
