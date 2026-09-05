import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import { applyPreferences, loadPreferences } from "./preferences";
import "./styles/tokens.css";
import "./styles/global.css";
import "./styles/components.css";
import "./styles/rev4.css";
import "./styles/themes.css";
applyPreferences(loadPreferences());
createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
