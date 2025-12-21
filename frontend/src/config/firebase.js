// Firebase configuration
export const firebaseConfig = {
  apiKey: "AIzaSyCC6k1b-K6bPTvl5BkpC217NzlmQ6AglWg",
  authDomain: "recruit-pro2.firebaseapp.com",
  projectId: "recruit-pro2",
  storageBucket: "recruit-pro2.firebasestorage.app",
  messagingSenderId: "787950188714",
  appId: "1:787950188714:web:82177f4d870fd8bc74b8d3",
  measurementId: "G-6SVYBTXPVM"
};

// API Base URL - Use environment variable or fallback to localhost
export const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
