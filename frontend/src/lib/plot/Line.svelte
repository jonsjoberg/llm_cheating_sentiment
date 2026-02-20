<script lang="ts">
	import type { SentimentPerDay, SentimentPerDaysAndApp } from '$lib/firebase_server';
	import { scaleLinear, scaleTime, type NumberValue } from 'd3-scale';
	import { line } from 'd3-shape';
	import tippy, { followCursor, type MultipleTargets } from 'tippy.js';
	const { overtimeSentiment }: { overtimeSentiment: SentimentPerDaysAndApp[] } = $props();

	function* dateGenerator(start: Date, end: Date, spacing: number) {
		let current = new Date(start);
		while (current <= end) {
			yield new Date(current);
			current.setDate(current.getDate() + spacing);
		}
	}

	function* yTickGenerator(min: number, max: number, spacing: number) {
		let current = min;
		while (current <= max) {
			yield current;
			current += spacing;
		}
	}

	const findFirstDate = (overtimeSentiment: SentimentPerDaysAndApp[]): Date[] => {
		let fDt = new Date();
		let lDt = new Date(0);

		overtimeSentiment.forEach((a) => {
			a.sentimentsPerDay.forEach((d) => {
				if (d.day < fDt) {
					fDt = d.day;
				}
				if (d.day > lDt) {
					lDt = d.day;
				}
			});
		});

		return [fDt, lDt];
	};

	const calculateResultingPct = (
		sentiment: SentimentPerDay
	): { date: Date; resultingPct: number } => {
		const resultingPct =
			(100 * (sentiment.reviewsPerSentiment.positive - sentiment.reviewsPerSentiment.negative)) /
			(sentiment.reviewsPerSentiment.positive +
				sentiment.reviewsPerSentiment.negative +
				sentiment.reviewsPerSentiment.notMentioned);
		return {
			date: sentiment.day,
			resultingPct: resultingPct
		};
	};

	const tooltip = (pd: PlotData) => {
		return (node: MultipleTargets) => {
			const tooltip = tippy(node, {
				content: pd.name,
				followCursor: true,
				plugins: [followCursor],
				theme: 'tomato'
			});
			return tooltip.destroy;
		};
	};

	type PlotData = {
		name: string;
		sentimentPerDay: {
			date: Date;
			resultingPct: number;
		}[];
	};

	const plotData: PlotData[] = $derived(
		overtimeSentiment.map((oS) => {
			return {
				name: oS.app.name,
				sentimentPerDay: oS.sentimentsPerDay
					.map((s) => calculateResultingPct(s))
					.filter((s) => !Number.isNaN(s.resultingPct))
			};
		})
	);

	const minMaxYValues = $derived(
		plotData.reduce(
			(acc, curr) => {
				const currMinMax = curr.sentimentPerDay.reduce(
					(a, c) => {
						return {
							min: c.resultingPct < a.min ? c.resultingPct : a.min,
							max: c.resultingPct > a.max ? c.resultingPct : a.max
						};
					},
					{
						min: curr.sentimentPerDay[0].resultingPct,
						max: curr.sentimentPerDay[0].resultingPct
					}
				);
				return {
					min: currMinMax.min < acc.min ? currMinMax.min : acc.min,
					max: currMinMax.max > acc.max ? currMinMax.max : acc.max
				};
			},
			{
				min: plotData[0].sentimentPerDay[0].resultingPct,
				max: plotData[0].sentimentPerDay[0].resultingPct
			}
		)
	);

	const width = $state(1000);
	const height = $state(500);
	const padding = 20;

	const firstAndLastDate = $derived(findFirstDate(overtimeSentiment));
	const xScale = $derived(
		scaleTime()
			.domain(firstAndLastDate)
			.range([padding, width - padding])
	);
	const xTicks = $derived([...dateGenerator(firstAndLastDate[0], firstAndLastDate[1], 7)]);

	const yScale = $derived(
		scaleLinear()
			.domain([minMaxYValues.max, minMaxYValues.min])
			.range([padding, height - padding * 2])
	);

	const ySpacing = $derived(minMaxYValues.max - minMaxYValues.min > 25 ? 5 : 1);
	const yTicks = $derived([...yTickGenerator(minMaxYValues.min, minMaxYValues.max, ySpacing)]);

	const lineGenerator = $derived(
		line()
			.x((d: { date: string | number | Date }) => xScale(new Date(d.date)))
			.y((d: { resultingPct: NumberValue }) => yScale(d.resultingPct))
	);

	let hoveredLine: string | null = $state(null);
</script>

<div class="chart">
	<svg {width} {height}>
		{#each xTicks as tick}
			<g transform="translate({xScale(tick)}, 0)" class="tick">
				<line y1="0" y2={height - 2 * padding} />
				<text y={height - padding} text-anchor="middle">{tick.toISOString().split('T')[0]}</text>
			</g>
		{/each}

		{#each yTicks as tick}
			<g transform="translate(0, {yScale(tick)})" class="tick">
				<line x1="0" x2={width} />
				<text x={width - padding} text-anchor="middle">{tick}</text>
			</g>
		{/each}
		{#each plotData as pd}
			<g class="line-group">
				<path
					{@attach tooltip(pd)}
					d={lineGenerator(pd.sentimentPerDay)}
					fill="none"
					stroke="transparent"
					stroke-width="15"
					onmouseenter={() => (hoveredLine = pd.name)}
					onmouseleave={() => (hoveredLine = null)}
					role="tooltip"
				/>
				<path
					class="line"
					class:lineHover={hoveredLine === pd.name}
					d={lineGenerator(pd.sentimentPerDay)}
					fill="none"
				/>
			</g>
		{/each}
	</svg>
	<div class="selectionBar">
		{#each overtimeSentiment as d}
			<button>{d.app.name}</button>
		{/each}
	</div>
</div>

<style>
	.chart {
		display: flex;
		flex-direction: column;
		align-items: center;
		width: 100%;
		gap: 2em;
	}
	.line {
		stroke: var(--main-color);
		stroke-width: 1px;
		stroke-dasharray: 2 2;
		z-index: 1;
	}
	.lineHover {
		stroke-width: 4px;
		stroke-dasharray: none;
		z-index: 99;
	}
	.selectionBar {
		display: flex;
		flex-direction: row;
		flex-wrap: wrap;
		gap: 1em 2em;
	}
</style>
