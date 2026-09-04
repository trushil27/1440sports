import { NextResponse, type NextRequest } from "next/server";

/**
 * Cheap pre-check: without the API's session cookie there is nothing to render, so
 * send the visitor to /signin before any page work. The API remains the authority
 * (an expired or forged cookie still gets a 401, handled by src/lib/api.ts).
 */
const SESSION_COOKIE = "intel_session";

export function middleware(req: NextRequest) {
  const { pathname, search } = req.nextUrl;
  if (req.cookies.has(SESSION_COOKIE)) return NextResponse.next();
  const url = req.nextUrl.clone();
  url.pathname = "/signin";
  url.search = pathname === "/" ? "" : `?next=${encodeURIComponent(pathname + search)}`;
  return NextResponse.redirect(url);
}

export const config = {
  matcher: [
    // Everything except: auth pages, the proxied API/auth routes, Next internals,
    // and static files (anything with an extension).
    "/((?!signin|enrol|api|auth|_next|sw\\.js|manifest\\.webmanifest|.*\\..*).*)",
  ],
};
