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

export const getSnapshotSentimentsPerApp = async (
	db: admin.firestore.Firestore,
	app: FBSteamApp,
	fromDate: Date
): Promise<AppReviewsPerSentiment> => {
	const toDate = new Date();

	const reviewsSummarized = await getSentimentPerDaysAndApp(db, app, fromDate, toDate);

	let positive = 0;
	let negative = 0;
	let notMentioned = 0;
	reviewsSummarized.sentimentsPerDay.forEach((r) => {
		positive += r.reviewsPerSentiment.positive ?? 0;
		negative += r.reviewsPerSentiment.negative ?? 0;
		notMentioned += r.reviewsPerSentiment.notMentioned ?? 0;
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

export type SentimentPerDay = {
	day: Date;
	reviewsPerSentiment: ReviewsPerSentiment;
};

export type SentimentPerDaysAndApp = {
	app: FBSteamApp;
	sentimentsPerDay: SentimentPerDay[];
};

export const getSentimentPerDaysAndApp = async (
	db: admin.firestore.Firestore,
	app: FBSteamApp,
	fromDate: Date | undefined = undefined,
	toDate: Date | undefined = undefined
): Promise<SentimentPerDaysAndApp> => {
	let reviewsPerDayQuery = db
		.collection('apps')
		.doc(`${app.appId}`)
		.collection('summarized_reviews')
		.orderBy(admin.firestore.FieldPath.documentId());

	if (fromDate != undefined)
		reviewsPerDayQuery = reviewsPerDayQuery.startAt(fromDate.toISOString().split('T')[0]);
	if (toDate != undefined)
		reviewsPerDayQuery = reviewsPerDayQuery.endAt(toDate.toISOString().split('T')[0]);

	const reviewsPerDay = await reviewsPerDayQuery.get();

	const sentimentsPerDay: SentimentPerDay[] = reviewsPerDay.docs.map((d) => {
		return {
			day: new Date(`${d.ref.id}T00:00:00`),
			reviewsPerSentiment: {
				positive: d.get(ReviewSentiment.Positive),
				negative: d.get(ReviewSentiment.Negative),
				notMentioned: d.get(ReviewSentiment.NotMentioned)
			}
		};
	});

	return {
		app: app,
		sentimentsPerDay: sentimentsPerDay
	};
};
