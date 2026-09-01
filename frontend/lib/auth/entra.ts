"use client";

import { InteractionRequiredAuthError, PublicClientApplication } from "@azure/msal-browser";

const enabled = process.env.NEXT_PUBLIC_AUTH_PROVIDER === "entra";
const clientId = process.env.NEXT_PUBLIC_AZURE_FRONTEND_CLIENT_ID ?? "";
const tenantId = process.env.NEXT_PUBLIC_AZURE_TENANT_ID ?? "";
const backendScope = process.env.NEXT_PUBLIC_AZURE_BACKEND_SCOPE ?? "";

export const entraEnabled = enabled;
export const msalInstance = new PublicClientApplication({
  auth: {
    clientId: clientId || "missing-client-id",
    authority: `https://login.microsoftonline.com/${tenantId || "common"}`,
    redirectUri: typeof window === "undefined" ? undefined : window.location.origin,
  },
  cache: { cacheLocation: "sessionStorage" },
});

let initialized: Promise<void> | null = null;
let accessTokenRequest: Promise<string> | null = null;

export function initializeEntra(): Promise<void> {
  if (!enabled) return Promise.resolve();
  if (!clientId || !tenantId || !backendScope) return Promise.reject(new Error("Falta configuración pública de Microsoft Entra."));
  if (!initialized) {
    initialized = msalInstance.initialize().then(async () => {
      const result = await msalInstance.handleRedirectPromise();
      if (result?.account) msalInstance.setActiveAccount(result.account);
      else if (!msalInstance.getActiveAccount() && msalInstance.getAllAccounts()[0]) msalInstance.setActiveAccount(msalInstance.getAllAccounts()[0]);
    });
  }
  return initialized;
}

export async function signIn(): Promise<void> {
  await initializeEntra();
  await msalInstance.loginRedirect({ scopes: [backendScope] });
}

export async function authorizationHeaders(): Promise<HeadersInit> {
  if (!enabled) {
    const userId = window.localStorage.getItem("academia-bid.development-user");
    return userId ? { "X-Dev-User-Id": userId } : {};
  }
  await initializeEntra();
  const account = msalInstance.getActiveAccount();
  if (!account) throw new Error("Inicia sesión con Microsoft Entra para continuar.");
  if (!accessTokenRequest) {
    accessTokenRequest = msalInstance.acquireTokenSilent({ account, scopes: [backendScope] })
      .then((token) => token.accessToken)
      .finally(() => { accessTokenRequest = null; });
  }
  try {
    return { Authorization: `Bearer ${await accessTokenRequest}` };
  } catch (error) {
    const errorCode = typeof error === "object" && error !== null && "errorCode" in error ? String(error.errorCode) : "";
    if (error instanceof InteractionRequiredAuthError || errorCode === "timed_out") {
      await msalInstance.acquireTokenRedirect({ account, scopes: [backendScope] });
    }
    throw error;
  }
}
