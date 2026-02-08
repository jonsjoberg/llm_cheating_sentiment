import type { PageServerLoad } from './$types';

import { db, getAllSentimentsPerApp, getSteamApps } from '$lib/firebase_server';

export const load: PageServerLoad = async () => {
	const lookback_window_days = 7;

	const apps = await getSteamApps(db!);

	const appsWithReviewsPromises = apps.map((a) => {
		return getAllSentimentsPerApp(db!, a, lookback_window_days);
	});
	const appsWithReviews = await Promise.all(appsWithReviewsPromises);

	return { appsWithReviews };
};
