import admin from 'firebase-admin';

import { PRIVATE_KEY, CLIENT_EMAIL, PROJECT_ID } from '$env/static/private';

const serviceAccount = {
	projectId: PROJECT_ID,
	clientEmail: CLIENT_EMAIL,
	privateKey: PRIVATE_KEY.replace(/\\n/g, '\n')
};

const getDb = (): admin.firestore.Firestore | undefined => {
	const db =
		admin.apps.length > 0
			? admin.apps[0]?.firestore()
			: admin
					.initializeApp({
						credential: admin.credential.cert(serviceAccount),
						databaseURL: `https://${serviceAccount.projectId}.firebaseio.com`
					})
					.firestore();
	return db;
};

export const db = getDb();

export type FBSteamApp = {
	appId: number;
	name: string;
};

export const getSteamApps = async (db: admin.firestore.Firestore): Promise<FBSteamApp[]> => {
	const fbApps = await db.collection('apps').select('app_id', 'name').get();

	const apps: FBSteamApp[] = [];
	if (fbApps.empty) {
		return apps;
	}
	fbApps.forEach((a) => {
		apps.push({ appId: a.get('app_id'), name: a.get('name') });
	});

	return apps;
};

enum ReviewSentiment {
	Positive = 'positive',
	Negative = 'negative',
	NotMentioned = 'not mentioned'
}

export type ReviewsPerSentiment = {
	positive: number;
	negative: number;
	notMentioned: number;
};

export type AppReviewsPerSentiment = {
	app: FBSteamApp;
	reviewsPerSentiment: ReviewsPerSentiment;
};

export const getAllSentimentsPerApp = async (
	db: admin.firestore.Firestore,
	app: FBSteamApp,
	lookback_window_days: number
): Promise<AppReviewsPerSentiment> => {
	const positive = getReviewsPerAppAndSentiment(
		db,
		app,
		ReviewSentiment.Positive,
		lookback_window_days
	);
	const negative = getReviewsPerAppAndSentiment(
		db,
		app,
		ReviewSentiment.Negative,
		lookback_window_days
	);
	const notMentioned = getReviewsPerAppAndSentiment(
		db,
		app,
		ReviewSentiment.NotMentioned,
		lookback_window_days
	);

	return {
		app,
		reviewsPerSentiment: {
			positive: await positive,
			negative: await negative,
			notMentioned: await notMentioned
		}
	};
};

export const getReviewsPerAppAndSentiment = async (
	db: admin.firestore.Firestore,
	app: FBSteamApp,
	sentiment: ReviewSentiment,
	lookback_window_days: number
): Promise<number> => {
	const fromDate = new Date(); // Today's date
	fromDate.setDate(fromDate.getDate() - lookback_window_days);

	const reviewsRef = db.collection('apps').doc(`${app.appId}`).collection('reviews');
	const reviewsWithSentiment = reviewsRef
		.where('timestamp_created', '>=', fromDate)
		.where('sentiment', '==', sentiment);
	const count = await reviewsWithSentiment.count().get();
	return count.data().count;
};
