/** Types for the environment variables the frontend reads (see `.env.example`). */
interface ImportMetaEnv {
  /** Where the browser sends API calls. `/api` in development (goes through the Vite proxy). */
  readonly VITE_API_BASE_URL?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
