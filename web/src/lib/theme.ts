export type Theme = "light" | "dark";

/**
 * Runs before hydration (inline in <head>). Stored choice wins; otherwise the default
 * is dark on a phone-sized viewport and light on desktop.
 */
export const THEME_INIT_SCRIPT = `(function(){try{var t=localStorage.getItem("theme");if(t!=="dark"&&t!=="light"){var m=window.matchMedia("(max-width: 767px)").matches;var l=window.matchMedia("(prefers-color-scheme: light)").matches;t=m&&!l?"dark":"light";}document.documentElement.setAttribute("data-theme",t);}catch(e){document.documentElement.setAttribute("data-theme","light");}})();`;

export function getTheme(): Theme {
  if (typeof document === "undefined") return "light";
  return document.documentElement.getAttribute("data-theme") === "dark" ? "dark" : "light";
}

export function setTheme(t: Theme) {
  document.documentElement.setAttribute("data-theme", t);
  try {
    localStorage.setItem("theme", t);
  } catch {
    /* private mode: the toggle still applies for this page */
  }
}
