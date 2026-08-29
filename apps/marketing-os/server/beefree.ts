export type BeefreeSession = { configured: boolean; accessToken?: string; message: string };

export async function createBeefreeSession(uid: string): Promise<BeefreeSession> {
  const clientId = process.env.BEE_CLIENT_ID;
  const clientSecret = process.env.BEE_CLIENT_SECRET;
  if (!clientId || !clientSecret) {
    return { configured: false, message: "Beefree credentials have not been configured for this environment." };
  }

  const response = await fetch("https://auth.getbee.io/loginV2", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ client_id: clientId, client_secret: clientSecret, uid }),
  });
  const payload = await response.json().catch(() => null) as { access_token?: string; v2?: boolean } | null;
  if (!response.ok || !payload?.access_token || payload.v2 !== true) {
    throw new Error("Beefree authentication failed. No credential data was exposed.");
  }

  return { configured: true, accessToken: payload.access_token, message: "Beefree editor session ready." };
}
