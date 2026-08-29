import { useEffect, useMemo, useState } from "react";
import { Builder, useBuilder, type IBeeConfig, type IToken } from "@beefree.io/react-email-builder";
import { Loader2, Save, ScanSearch, ShieldAlert } from "lucide-react";
import { Button } from "@/components/ui/button";
import { trpc } from "@/lib/trpc";
import { useAuth } from "@/_core/hooks/useAuth";
import { activeEditorProvider } from "@/lib/editorProvider";

type BeefreeWorkspaceProps = {
  emailKey: string;
  subject: string;
  previewText: string;
};

const emptyTemplate = { comments: {}, page: {} } as never;

export function BeefreeWorkspace({ emailKey, subject, previewText }: BeefreeWorkspaceProps) {
  const { isAuthenticated, user } = useAuth();
  const [token, setToken] = useState<IToken | null>(null);
  const [status, setStatus] = useState("Editor requires a secure server session.");
  const [exportedHtml, setExportedHtml] = useState("");
  const session = trpc.campaigns.beefree.session.useQuery(
    { uid: `campaign-os-${user?.id ?? "preview"}` },
    { enabled: isAuthenticated, retry: false },
  );
  const saveRevision = trpc.campaigns.revisions.save.useMutation({
    onSuccess: () => setStatus("Revision stored with canonical provenance."),
    onError: error => setStatus(error.message),
  });
  const config = useMemo<IBeeConfig>(() => ({
    container: "beefree-editor-canvas",
    uid: `campaign-os-${user?.id ?? "preview"}`,
    language: "en-US",
  }), [user?.id]);
  const { id, save, preview, updateToken } = useBuilder(config);

  useEffect(() => {
    const nextToken = session.data?.accessToken;
    if (!nextToken) return;
    const typedToken = { access_token: nextToken, v2: true } as IToken;
    setToken(typedToken);
    void updateToken(typedToken);
    setStatus("Secure Beefree session ready.");
  }, [session.data?.accessToken, updateToken]);

  if (!isAuthenticated) {
    return (
      <section className="editor-unavailable">
        <ShieldAlert className="h-5 w-5" />
        <div>
          <p className="font-medium">Editor access is protected</p>
          <p>Sign in to create a server-issued Beefree session. Canonical source remains available in read-only mode.</p>
        </div>
      </section>
    );
  }

  if (session.isLoading || (!token && !session.isError)) {
    return <section className="editor-unavailable"><Loader2 className="h-5 w-5 animate-spin" /><p>Issuing a short-lived editor session…</p></section>;
  }

  if (session.isError || !token) {
    return (
      <section className="editor-unavailable editor-unavailable-warning">
        <ShieldAlert className="h-5 w-5" />
        <div>
          <p className="font-medium">Beefree is not configured in this environment</p>
          <p>{session.error?.message || session.data?.message || "Provide server-side Beefree credentials to enable the editor."}</p>
        </div>
      </section>
    );
  }

  return (
    <section className="editor-wrap">
      <div className="editor-toolbar">
        <div>
          <p className="eyebrow">Provider adapter · {activeEditorProvider.label}</p>
          <p className="editor-status">{status}</p>
        </div>
        <div className="toolbar-actions">
          <Button variant="outline" onClick={() => void preview()}><ScanSearch className="mr-2 h-4 w-4" />Preview</Button>
          <Button onClick={() => void save()} disabled={saveRevision.isPending}><Save className="mr-2 h-4 w-4" />Save revision</Button>
        </div>
      </div>
      <div className="editor-canvas">
        <Builder
          id={id}
          token={token}
          template={emptyTemplate}
          width="100%"
          height="720px"
          onLoad={() => setStatus("Beefree workspace ready. Saving creates an immutable Campaign OS revision.")}
          onError={error => setStatus(`Beefree error ${error.code}: ${error.message}`)}
          onSave={(pageJson, pageHtml) => {
            setExportedHtml(pageHtml);
            saveRevision.mutate({
              emailKey,
              providerDocument: pageJson,
              renderedHtml: pageHtml,
              subject,
              previewText,
            });
          }}
        />
      </div>
      {exportedHtml ? <p className="editor-evidence">Latest HTML is held in memory until the revision mutation completes; the server persists the approved export and provider document together.</p> : null}
    </section>
  );
}
