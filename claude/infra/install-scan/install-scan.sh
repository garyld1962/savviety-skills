#!/usr/bin/env bash
# Install Scan Hook — PostToolUse on Bash matching package install commands.
#
# After the agent runs any of:
#   brew install / brew upgrade
#   pip install / pip3 install / python3 -m pip install
#   npm install / npm i / yarn add / pnpm add
#   dotnet tool install / dotnet add package
#   gh extension install
#   cargo install / cargo add
#   gem install
#   apt install / apt-get install
#
# this hook scans the named packages against OSV.dev (Google's federated
# vulnerability database — covers NVD + GHSA + ecosystem advisories) and
# prints findings (CVE-IDs, severity, summary, fix version) inline so the
# user sees them in chat without opening a log file.
#
# Detection only — never blocks. Use a PreToolUse hook for blocking.
# Always exits 0 (fail-open) so scan failures never break the agent.
#
# Install: see install-scan/INSTALL.md.

set +e
exec 3>&2
exec 2>/dev/null

PAYLOAD=$(cat)
[ -n "$PAYLOAD" ] || exit 0

TOOL=$(echo "$PAYLOAD" | jq -r '(.tool_name // .toolName // "unknown")')
[ "$TOOL" = "Bash" ] || exit 0

COMMAND=$(echo "$PAYLOAD" | jq -r '(.tool_input.command // .toolInput.command // "")')
[ -n "$COMMAND" ] || exit 0

NORM=$(echo "$COMMAND" | sed -E 's/^(sudo|env [A-Z_=]+)+ +//; s/^[[:space:]]+//')

PM=""; ECOSYSTEM=""; PACKAGES=""

case "$NORM" in
  brew\ install\ *|brew\ upgrade\ *)
    PM="brew"; ECOSYSTEM="Homebrew"
    PACKAGES=$(echo "$NORM" | sed -E 's/^brew (install|upgrade) +//' | tr -s ' ' '\n' | grep -vE '^(--|-)' | tr '\n' ' ')
    ;;
  pip\ install\ *|pip3\ install\ *|python\ -m\ pip\ install\ *|python3\ -m\ pip\ install\ *)
    PM="pip"; ECOSYSTEM="PyPI"
    PACKAGES=$(echo "$NORM" | sed -E 's/^(python3? -m )?pip3? install +//' | tr -s ' ' '\n' | grep -vE '^(--|-)' | tr '\n' ' ')
    ;;
  npm\ install\ *|npm\ i\ *|npm\ add\ *|yarn\ add\ *|pnpm\ add\ *|pnpm\ install\ *)
    PM="npm"; ECOSYSTEM="npm"
    PACKAGES=$(echo "$NORM" | sed -E 's/^(npm (install|i|add)|yarn add|pnpm (add|install)) +//' | tr -s ' ' '\n' | grep -vE '^(--|-)' | tr '\n' ' ')
    ;;
  dotnet\ tool\ install\ *|dotnet\ add\ package\ *)
    PM="dotnet"; ECOSYSTEM="NuGet"
    PACKAGES=$(echo "$NORM" | sed -E 's/^dotnet (tool install|add package) +//' | tr -s ' ' '\n' | grep -vE '^(--|-)' | head -1)
    ;;
  cargo\ install\ *|cargo\ add\ *)
    PM="cargo"; ECOSYSTEM="crates.io"
    PACKAGES=$(echo "$NORM" | sed -E 's/^cargo (install|add) +//' | tr -s ' ' '\n' | grep -vE '^(--|-)' | tr '\n' ' ')
    ;;
  gem\ install\ *)
    PM="gem"; ECOSYSTEM="RubyGems"
    PACKAGES=$(echo "$NORM" | sed -E 's/^gem install +//' | tr -s ' ' '\n' | grep -vE '^(--|-)' | tr '\n' ' ')
    ;;
  gh\ extension\ install\ *)
    PM="gh"; ECOSYSTEM="github-extension"
    PACKAGES=$(echo "$NORM" | sed -E 's/^gh extension install +//' | tr -s ' ' '\n' | head -1)
    ;;
  apt\ install\ *|apt-get\ install\ *)
    PM="apt"; ECOSYSTEM="Debian"
    PACKAGES=$(echo "$NORM" | sed -E 's/^apt(-get)? install +//' | tr -s ' ' '\n' | grep -vE '^(--|-y|-q)' | tr '\n' ' ')
    ;;
  *)
    exit 0
    ;;
esac

PACKAGES=$(echo "$PACKAGES" | tr -s ' ')
[ -z "$PACKAGES" ] && exit 0

# ─── Load CISA KEV (Known Exploited Vulnerabilities) catalog ───
# Cached for 6 hours under /tmp; falls back to skipping the overlay if offline.
KEV_CACHE="/tmp/cisa-kev-cache.json"
KEV_TTL_SEC=21600     # 6 hours

if [ ! -f "$KEV_CACHE" ] || [ "$(($(date +%s) - $(stat -f %m "$KEV_CACHE" 2>/dev/null || stat -c %Y "$KEV_CACHE" 2>/dev/null || echo 0)))" -gt "$KEV_TTL_SEC" ]; then
  curl -s -m 8 "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json" -o "$KEV_CACHE.tmp" 2>/dev/null
  [ -s "$KEV_CACHE.tmp" ] && mv "$KEV_CACHE.tmp" "$KEV_CACHE" || rm -f "$KEV_CACHE.tmp"
fi

is_kev_cve() {
  local cve="$1"
  [ -f "$KEV_CACHE" ] || return 1
  jq -e --arg cve "$cve" '.vulnerabilities[]? | select(.cveID==$cve)' "$KEV_CACHE" >/dev/null 2>&1
}

{
  echo ""
  echo "──── 🔒 install-scan ($PM → $ECOSYSTEM) ────"
  echo "Packages: $PACKAGES"
  echo ""
  TOTAL_HITS=0
  TOTAL_HIGH=0
  TOTAL_KEV=0
  for pkg in $PACKAGES; do
    name=$(echo "$pkg" | sed -E 's/[<>=~!@].*//')
    ver=$(echo "$pkg" | sed -nE 's/.*[<>=~!@]+([0-9][0-9a-zA-Z.\-]*).*/\1/p')
    [ -z "$name" ] && continue

    if [ -n "$ver" ]; then
      QUERY="{\"package\":{\"name\":\"$name\",\"ecosystem\":\"$ECOSYSTEM\"},\"version\":\"$ver\"}"
    else
      QUERY="{\"package\":{\"name\":\"$name\",\"ecosystem\":\"$ECOSYSTEM\"}}"
    fi

    RESP=$(curl -s -m 8 -X POST "https://api.osv.dev/v1/query" \
      -H "Content-Type: application/json" -d "$QUERY" 2>/dev/null)

    if [ -z "$RESP" ]; then
      echo "  ? $name${ver:+@$ver} — scan failed (network?)"
      continue
    fi

    VULN_LINES=$(echo "$RESP" | jq -r '
      (.vulns // [])[] |
      [.id,
       (.summary // .details // "" | gsub("\n"; " ") | .[0:90]),
       (.database_specific.severity // ""),
       ([.affected[]?.ranges[]?.events[]? | select(has("fixed")) | .fixed] | join(", ")),
       ([.aliases[]? | select(startswith("CVE-"))] | join(","))
      ] | @tsv
    ' 2>/dev/null)

    if [ -z "$VULN_LINES" ]; then
      echo "  ✓ $name${ver:+@$ver} — clean"
    else
      COUNT=$(echo "$VULN_LINES" | wc -l | tr -d ' ')
      HIGH=$(echo "$VULN_LINES" | awk -F'\t' 'BEGIN{c=0} $3=="HIGH"||$3=="CRITICAL"{c++} END{print c}')
      TOTAL_HITS=$((TOTAL_HITS + COUNT))
      TOTAL_HIGH=$((TOTAL_HIGH + HIGH))

      echo "  ⚠ $name${ver:+@$ver} — $COUNT vulnerabilit$([ "$COUNT" = "1" ] && echo "y" || echo "ies")${HIGH:+ ($HIGH high/critical)}:"
      echo "$VULN_LINES" | head -8 | while IFS=$'\t' read -r id summary severity fix cves; do
        sev_tag=""
        [ -n "$severity" ] && sev_tag=" [$severity]"
        fix_tag=""
        [ -n "$fix" ] && fix_tag=" → fixed in $fix"
        kev_tag=""
        # CISA KEV check — if any aliased CVE is in the catalog, flag actively-exploited
        if [ -n "$cves" ]; then
          IFS=',' read -ra CVE_ARR <<< "$cves"
          for cve in "${CVE_ARR[@]}"; do
            if is_kev_cve "$cve"; then
              kev_tag=" 🔥 ACTIVELY EXPLOITED (CISA KEV: $cve)"
              TOTAL_KEV=$((TOTAL_KEV + 1))
              break
            fi
          done
        fi
        echo "      • $id$sev_tag$fix_tag$kev_tag"
        [ -n "$summary" ] && echo "        $summary"
      done
      if [ "$COUNT" -gt 8 ]; then
        echo "      … and $((COUNT - 8)) more"
      fi
      echo ""
    fi
  done

  echo ""
  if [ "$TOTAL_HITS" -eq 0 ]; then
    echo "✓ No known vulnerabilities."
  else
    echo "Summary: $TOTAL_HITS findings ($TOTAL_HIGH high/critical, $TOTAL_KEV CISA KEV actively-exploited)"
    echo "Sources: OSV.dev (NVD + GHSA + ecosystem advisories) + CISA KEV catalog"
    [ "$TOTAL_KEV" -gt 0 ] && echo "🔥 CISA KEV findings indicate confirmed active exploitation. Treat as urgent."
  fi
  echo "────────────────────────────────────"
  echo ""
} >&3

exit 0
