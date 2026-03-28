#!/usr/bin/env bash
set -Eeuo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DOCS_DIR="${APP_DIR}/docs"

mkdir -p "$DOCS_DIR"

if command -v curl >/dev/null 2>&1; then
  DOWNLOADER="curl"
elif command -v wget >/dev/null 2>&1; then
  DOWNLOADER="wget"
else
  echo "Install curl or wget first."
  exit 1
fi

download() {
  local url="$1"
  local output="$2"

  echo "==> Downloading $(basename "$output")"
  if [ "$DOWNLOADER" = "curl" ]; then
    curl -L --fail --show-error --silent "$url" -o "$output"
  else
    wget -q -O "$output" "$url"
  fi
}

# Prioritas: dokumen tindakan/kesiapsiagaan yang paling berguna untuk chatbot publik.
download \
  "https://www.bnpb.go.id/storage/app/media/uploads/24/buku-data-bencana/6-buku-saku-cetakan-4-2019.pdf" \
  "$DOCS_DIR/01-bnpb-buku-saku-bencana-2019.pdf"

download \
  "https://pusatkrisis.kemkes.go.id/__pub/files49279Final_Pedoman_Nasional_Penanggulangan_Krisis_Kesehatan.pdf" \
  "$DOCS_DIR/02-kemkes-pedoman-nasional-penanggulangan-krisis-kesehatan-2023.pdf"

download \
  "https://content.bmkg.go.id/wp-content/uploads/Panduan-Implementasi-Tsunami-Ready-Recognition-Program.pdf" \
  "$DOCS_DIR/03-bmkg-panduan-implementasi-tsunami-ready.pdf"

download \
  "https://content.bmkg.go.id/wp-content/uploads/Tsunami-Ready-Kit-Panduan-Teknis-Komunitas-Tsunami-Ready.pdf" \
  "$DOCS_DIR/04-bmkg-tsunami-ready-kit-panduan-teknis.pdf"

echo
echo "Downloaded priority documents into: $DOCS_DIR"
ls -lh "$DOCS_DIR"
