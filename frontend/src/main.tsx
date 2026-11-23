/** Starts the React app inside <div id="root"> in index.html. */
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import { HealthPage } from "./pages/HealthPage";

const root = document.getElementById("root");
if (!root) throw new Error("index.html has no #root element");

createRoot(root).render(
  <StrictMode>
    <HealthPage />
  </StrictMode>,
);
