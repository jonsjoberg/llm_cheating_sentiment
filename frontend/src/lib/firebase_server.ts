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
	const fromDate = new Date();
	fromDate.setDate(fromDate.getDate() - lookback_window_days);
	const toDate = new Date();

	const reviewsSummarized = await db
		.collection('apps')
		.doc(`${app.appId}`)
		.collection('summarized_reviews')
		.orderBy(admin.firestore.FieldPath.documentId())
		.startAt(fromDate.toISOString().split('T')[0])
		.endAt(toDate.toISOString().split('T')[0])
		.get();

	let positive = 0;
	let negative = 0;
	let notMentioned = 0;
	reviewsSummarized.forEach((r) => {
		positive += r.get(ReviewSentiment.Positive);
		negative += r.get(ReviewSentiment.Negative);
		notMentioned += r.get(ReviewSentiment.NotMentioned);
	});

	return {
		app,
		reviewsPerSentiment: {
			positive: positive,
			negative: negative,
			notMentioned: notMentioned
		}
	};
};
