<script lang="ts">
	import type { SentimentPerDay, SentimentPerDaysAndApp } from '$lib/firebase_server';
	import { scaleLinear, scaleTime, type NumberValue } from 'd3-scale';
	import { line } from 'd3-shape';
	import tippy, { followCursor, type MultipleTargets } from 'tippy.js';
	import Label from './Label.svelte';
	const { overtimeSentiment }: { overtimeSentiment: SentimentPerDaysAndApp[] } = $props();

	function* dateGenerator(start: Date, end: Date, spacing: number) {
		let current = new Date(start);
		while (current <= end) {
			yield new Date(current);
			current.setDate(current.getDate() + spacing);
		}
	}

	function* yTickGenerator(min: number, max: number, spacing: number) {
		let current = Math.floor(min);
		while (current <= Math.ceil(max)) {
			yield Math.round(current);
			current += spacing;
		}
	}

	const findFirstDate = (plotData: PlotData[]): Date[] => {
		let fDt = new Date();
		let lDt = new Date(0);

		plotData.forEach((pd) => {
			pd.sentimentPerDay.forEach((d) => {
				if (d.date < fDt) {
					fDt = d.date;
				}
				if (d.date > lDt) {
					lDt = d.date;
				}
			});
		});

		return [fDt, lDt];
	};

	const shouldBeDisabled = (appName: string): boolean => {
		return plotData.filter((pd) => pd.name === appName).length === 0;
	};

	const calculateResultingPct = (
		sentiment: SentimentPerDay[]
	): { date: Date; resultingPct: number | null } => {
		const netSentiment = sentiment.reduce((a, s) => {
			return a + s.reviewsPerSentiment.positive - s.reviewsPerSentiment.negative;
		}, 0);

		const totalReviews = sentiment.reduce((a, s) => {
			return (
				a +
				s.reviewsPerSentiment.positive +
				s.reviewsPerSentiment.negative +
				s.reviewsPerSentiment.notMentioned
			);
		}, 0);

		let resultingPct = null;
		if (totalReviews > 0) {
			resultingPct = (100 * netSentiment) / totalReviews;
		}

		return {
			date: sentiment.at(-1)!.day,
			resultingPct: resultingPct
		};
	};

	const tooltip = (pd: PlotData) => {
		return (node: MultipleTargets) => {
			const tooltip = tippy(node, {
				content: pd.name,
				followCursor: true,
				plugins: [followCursor],
				theme: 'tomato',
				animation: 'myFade',
				duration: 500
			});
			return tooltip.destroy;
		};
	};

	const toggleSelectedLine = (appName: string) => {
		const index = selectedLines.indexOf(appName);

		if (index === -1) {
			selectedLines.push(appName);
		} else {
			selectedLines.splice(index, 1); // Removes 1 item at 'index'
		}
	};

	const anyLineHighlighted = (appName: string): boolean => {
		if (hoveredLine === appName || selectedLines.includes(appName)) {
			return false;
		}

		const hoverPredicate = hoveredLine !== appName && hoveredLine != null;
		const selectedPredicate = selectedLines.length > 0 && !selectedLines.includes(appName);

		return hoverPredicate || selectedPredicate;
	};

	const calculateMinMaxYValues = (plotData: PlotData[]): { min: number; max: number } => {
		if (plotData.length === 0) {
			return { min: 0, max: 1 };
		}

		return plotData.reduce(
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
		);
	};

	const rollingAvg = (windowDays: number, overtimeSentiment: SentimentPerDaysAndApp[]) => {
		const plotData = overtimeSentiment.map((oS) => {
			const res = [];
			for (let i = windowDays; i < oS.sentimentsPerDay.length; i++) {
				const currentResult = calculateResultingPct(oS.sentimentsPerDay.slice(i - windowDays, i));
				if (currentResult.resultingPct != null) {
					res.push(currentResult);
				}
			}

			return {
				name: oS.app.name,
				sentimentPerDay: res
			};
		});

		return plotData.filter((pd) => pd.sentimentPerDay.length > 0);
	};

	type PlotData = {
		name: string;
		sentimentPerDay: {
			date: Date;
			resultingPct: number;
		}[];
	};

	let rollingDayWindow = $state(1);
	let plotData: PlotData[] = $derived(rollingAvg(rollingDayWindow, overtimeSentiment));
	$inspect(plotData);

	const minMaxYValues = $derived(calculateMinMaxYValues(plotData));

	const width = $state(1000);
	const height = $state(500);
	const padding = 20;

	const firstAndLastDate = $derived(findFirstDate(plotData));
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

	const handleRollingAvgChange = (newSetting: string) => {
		console.log(newSetting);
		rollingDayWindowActive = newSetting;

		switch (newSetting) {
			case 'none':
				customRollingAvg = null;
				rollingDayWindow = 1;
				break;
			case 'week':
				customRollingAvg = null;
				rollingDayWindow = 7;
				break;
			case 'custom':
				rollingDayWindow = customRollingAvg ?? 1;
				break;
		}
	};

	let hoveredLine: string | null = $state(null);
	let selectedLines: string[] = $state([]);
	let rollingDayWindowActive = $state('week');
	let customRollingAvg = $state(null);
	$inspect(rollingDayWindow);
</script>

<div class="chart">
	<div class="selectionBar">
		{#each overtimeSentiment as d}
			<button
				disabled={shouldBeDisabled(d.app.name)}
				onclick={() => toggleSelectedLine(d.app.name)}
				onmouseenter={() => {
					if (!shouldBeDisabled(d.app.name)) hoveredLine = d.app.name;
				}}
				onmouseleave={() => (hoveredLine = null)}
				class:selectedButton={selectedLines.includes(d.app.name) && !shouldBeDisabled(d.app.name)}
			>
				{d.app.name}
			</button>
		{/each}
	</div>
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
					class:lineHover={hoveredLine === pd.name || selectedLines.includes(pd.name)}
					class:anyHover={anyLineHighlighted(pd.name)}
					d={lineGenerator(pd.sentimentPerDay)}
					fill="none"
				/>
				{#if selectedLines.includes(pd.name)}
					<g
						transform="translate(
						{xScale(pd.sentimentPerDay[0].date)}, 
						{yScale(pd.sentimentPerDay[0].resultingPct) + 20})"
					>
						<Label text={pd.name} />
					</g>
				{/if}
			</g>
		{/each}
	</svg>
	<div>
		Rolling Average:
		<button
			class:selectedButton={rollingDayWindowActive === 'none'}
			onclick={() => {
				handleRollingAvgChange('none');
			}}
		>
			None
		</button>
		<button
			class:selectedButton={rollingDayWindowActive === 'week'}
			onclick={() => {
				handleRollingAvgChange('week');
			}}
		>
			1 week
		</button>
		<span class="customRollingAvg" class:selectedButton={rollingDayWindowActive === 'custom'}>
			Custom: <input
				type="number"
				bind:value={customRollingAvg}
				oninput={() => handleRollingAvgChange('custom')}
				onblur={() => {
					if (customRollingAvg == null) rollingDayWindowActive = 'none';
				}}
			/> days</span
		>
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
		stroke-width: 1.5px;
		/* stroke-dasharray: 2 2; */
		z-index: 1;
		transition:
			stroke-width 1s ease,
			opacity 1s ease;
	}
	.lineHover {
		stroke-width: 5px;
		stroke-dasharray: none;
		stroke: var(--main-color);
		pointer-events: none;
		z-index: 99;
	}
	.anyHover {
		opacity: 0.25;
	}
	.selectionBar {
		display: flex;
		flex-direction: row;
		flex-wrap: wrap;
		gap: 1em 2em;
	}
	.selectedButton {
		background-color: var(--background-selected);
	}
	.customRollingAvg {
		border: 1px solid var(--main-color);
		padding: 0.25em 1.25em;
	}
	.customRollingAvg input {
		width: 2em;
		font-family: 'Silkscreen', sans-serif;
		font-weight: 400;
		font-style: normal;
		font-size: 14px;
		padding: 0;
		border: 1px solid var(--main-color);
	}
</style>
