import type { PageServerLoad } from './$types';

import { db, getAllSentimentsPerApp, getSteamApps } from '$lib/firebase_server';

export const load: PageServerLoad = async () => {
	const apps = await getSteamApps(db!);

	const appsWithReviewsPromises = apps.map((a) => {
		return getAllSentimentsPerApp(db!, a);
	});
	const appsWithReviews = await Promise.all(appsWithReviewsPromises);

	return { appsWithReviews };
};
