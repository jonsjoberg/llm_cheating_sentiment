import type { PageServerLoad } from './$types';

import {
	db,
	getSentimentPerDaysAndApp,
	getSnapshotSentimentsPerApp,
	getSteamApps,
	type AppReviewsPerSentiment,
	type SentimentPerDaysAndApp
} from '$lib/firebase_server';

export const load: PageServerLoad = async () => {
	const snapshotLookbackWindowDays = 7;
	const snapshotFromDate = new Date();
	snapshotFromDate.setDate(snapshotFromDate.getDate() - snapshotLookbackWindowDays);

	const overTimeLookbackWindowDays = 180;
	const overTimeFromDate = new Date();
	overTimeFromDate.setDate(overTimeFromDate.getDate() - overTimeLookbackWindowDays);

	const apps = await getSteamApps(db!);

	const snaphotsPromises: Promise<AppReviewsPerSentiment>[] = [];
	const overTimesPromises: Promise<SentimentPerDaysAndApp>[] = [];

	apps.forEach((a) => {
		snaphotsPromises.push(getSnapshotSentimentsPerApp(db!, a, snapshotFromDate));
		overTimesPromises.push(getSentimentPerDaysAndApp(db!, a, overTimeFromDate));
	});

	const appsWithReviews = await Promise.all(snaphotsPromises);
	const overtimeSentiment = await Promise.all(overTimesPromises);

	return { appsWithReviews, overtimeSentiment };
};
