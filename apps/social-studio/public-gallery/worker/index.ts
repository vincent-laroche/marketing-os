interface AssetFetcher {
  fetch(request: Request): Promise<Response>;
}

interface PublicGalleryEnv {
  ASSETS: AssetFetcher;
}

function withSecurityHeaders(response: Response): Response {
  const headers = new Headers(response.headers);
  headers.set("X-Robots-Tag", "noindex, nofollow");
  headers.set("X-Content-Type-Options", "nosniff");
  headers.set("Referrer-Policy", "no-referrer");
  headers.set("Permissions-Policy", "camera=(), microphone=(), geolocation=(), payment=()");
  headers.set("Content-Security-Policy", "default-src 'self'; img-src 'self' https://assets.hairsolutions.co; style-src 'self'; script-src 'self'; connect-src 'none'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'");

  if (headers.get("content-type")?.includes("text/html")) {
    headers.set("Cache-Control", "public, max-age=60, must-revalidate");
  }

  return new Response(response.body, { status: response.status, statusText: response.statusText, headers });
}

export default {
  async fetch(request: Request, env: PublicGalleryEnv): Promise<Response> {
    const response = await env.ASSETS.fetch(request);
    return withSecurityHeaders(response);
  }
} satisfies ExportedHandler<PublicGalleryEnv>;
