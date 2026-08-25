#!/usr/bin/env bash
# Authenticate mail.hairsolutions.co for MailerLite (account 2582639, domain id 1812088).
#
# Two changes:
#   1. ADD   CNAME litesrv._domainkey.mail.hairsolutions.co -> litesrv._domainkey.mlsend.com
#   2. EDIT  TXT   mail.hairsolutions.co  (append MailerLite's SPF include, keep HubSpot's)
#
# HubSpot's include stays first and unmodified. Resend is untouched: it uses its own
# selector (resend._domainkey.mail) and its own subdomain (send.mail.hairsolutions.co).
#
# Run:  bash dns/APPLY-MAILERLITE-DNS.sh
set -euo pipefail

set -a && source ~/.env && set +a
T="$CLOUDFLARE_API_KEY"                      # note: the MASTER token lacks DNS scope; this one has it
Z=44c9e2d6eb71ce0de6bb40e563bbf351           # hairsolutions.co
SPF_ID=32a229a095d790ae3c7eeaaa0676c5f0      # existing TXT on mail.hairsolutions.co

SPF_BEFORE='v=spf1 include:50966981.spf10.hubspotemail.net ~all'
SPF_AFTER='v=spf1 include:50966981.spf10.hubspotemail.net include:_spf.mlsend.com ~all'

echo "== 1/2  ADD DKIM CNAME =="
curl -s -X POST \
  -H "Authorization: Bearer $T" -H "Content-Type: application/json" \
  "https://api.cloudflare.com/client/v4/zones/$Z/dns_records" \
  --data '{"type":"CNAME","name":"litesrv._domainkey.mail.hairsolutions.co","content":"litesrv._domainkey.mlsend.com","ttl":1,"proxied":false}' \
  | python3 -c "import sys,json;d=json.load(sys.stdin);r=d.get('result') or {};print(' success:',d.get('success'),'| id:',r.get('id'));print(' errors :',d.get('errors'))"

echo "== 2/2  EDIT SPF (merge MailerLite include) =="
curl -s -X PATCH \
  -H "Authorization: Bearer $T" -H "Content-Type: application/json" \
  "https://api.cloudflare.com/client/v4/zones/$Z/dns_records/$SPF_ID" \
  --data "{\"content\":\"$SPF_AFTER\"}" \
  | python3 -c "import sys,json;d=json.load(sys.stdin);r=d.get('result') or {};print(' success:',d.get('success'));print(' content:',r.get('content'));print(' errors :',d.get('errors'))"

echo
echo "== verify (allow ~1-2 min for propagation) =="
sleep 20
echo -n "  SPF   : "; dig +short TXT mail.hairsolutions.co @1.1.1.1
echo -n "  DKIM  : "; dig +short CNAME litesrv._domainkey.mail.hairsolutions.co @1.1.1.1

cat <<'ROLLBACK'

== ROLLBACK — OBSOLETE as of 2026-08-19 ==
  HubSpot is fully removed from this zone; do NOT restore its SPF include.
  See HUBSPOT-DNS-REMOVAL.md.
  SPF restore:
    curl -X PATCH -H "Authorization: Bearer $CLOUDFLARE_API_KEY" -H "Content-Type: application/json" \
      "https://api.cloudflare.com/client/v4/zones/44c9e2d6eb71ce0de6bb40e563bbf351/dns_records/32a229a095d790ae3c7eeaaa0676c5f0" \
      --data '{"content":"v=spf1 include:50966981.spf10.hubspotemail.net ~all"}'
  DKIM: delete the litesrv._domainkey.mail.hairsolutions.co CNAME in the Cloudflare dashboard.
ROLLBACK
