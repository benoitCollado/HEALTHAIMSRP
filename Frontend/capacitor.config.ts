import type { CapacitorConfig } from '@capacitor/cli';

const serverUrl = process.env.CAPACITOR_SERVER_URL;
const isDev = process.env.NODE_ENV !== 'production';

const config: CapacitorConfig = {
  appId: 'com.healthai.app',
  appName: 'HealthAI',
  webDir: 'dist',
  ...(serverUrl ? { server: { url: serverUrl, cleartext: isDev } } : {})
};

export default config;
