import { initializeApp } from 'firebase/app';

export const firebaseConfig = {
	apiKey: 'AIzaSyD1o2_IooehbTPjS8_kCoq8b4tYx9CnD18',
	authDomain: 'cheating-sentiment.firebaseapp.com',
	projectId: 'cheating-sentiment',
	storageBucket: 'cheating-sentiment.firebasestorage.app',
	messagingSenderId: '705183632286',
	appId: '1:705183632286:web:3b207e82fe6195f4af648f'
};

// Initialize Firebase
export const FirebaseClient = initializeApp(firebaseConfig);
