---
{
  "schema": "wellmanifest.docs/document/v1",
  "id": "org-metadata-sync",
  "kind": "information",
  "version": 1,
  "title": "Centralna synchronizacja metadanych repozytorium",
  "status": "implemented",
  "owner": "autogrammar/toonic",
  "created": "2026-09-06",
  "updated": "2026-09-06",
  "review_after": "2026-10-06",
  "source_revision": "433e3e61fccb3523ee17b7008b6210841acaa3c0",
  "affected_repositories": [
    "autogrammar/toonic"
  ],
  "evidence": [
    "https://github.com/semcod/.github/blob/406fb4b692680b3d69d25ee9570e81869afbd0c5/org-sync/managed-repositories.json",
    "https://github.com/semcod/.github/pull/1"
  ]
}
---

# Centralna synchronizacja metadanych repozytorium

<!-- docs:section purpose -->
## Cel

Opis i tematy GitHub repozytorium `autogrammar/toonic` synchronizuje koordynator `semcod/.github`.

<!-- docs:section scope -->
## Zakres

Ten dokument opisuje obsługę metadanych tego repozytorium. Aktualizacja zależności i testy projektu mają osobne workflow.

<!-- docs:section evidence -->
## Dowody

Repozytorium jest jawnie wpisane do [katalogu koordynatora](https://github.com/semcod/.github/blob/406fb4b692680b3d69d25ee9570e81869afbd0c5/org-sync/managed-repositories.json). Zmianę mechanizmu opublikowano w [PR 1 koordynatora](https://github.com/semcod/.github/pull/1). [Wykonanie synchronizacji](https://github.com/semcod/.github/actions/runs/33996279028) zakończyło się sukcesem; ponowny odczyt API potwierdził temat `autogrammar` i zachowanie adresu WWW. Pełną konfigurację opisuje [instrukcja koordynatora](https://github.com/semcod/.github/blob/406fb4b692680b3d69d25ee9570e81869afbd0c5/docs/information/org-metadata-sync.md).

<!-- docs:section content -->
## Działanie

Centralny harmonogram `17 */6 * * *` uruchamia aktualizację co sześć godzin. Koordynator używa pełnej tożsamości `autogrammar/toonic` i własnego uwierzytelniania. Lokalny wyzwalacz `trigger-org-sync.yml`, który wymagał niedostępnego sekretu `ORG_SYNC_PAT`, został wycofany.

Tryb `--metadata-only --skip-profile` aktualizuje opis i tematy, zachowując adres WWW, konfigurację GitHub Pages i profil organizacji. Lokalny sekret `ORG_SYNC_PAT` nie jest potrzebny.

Operator z dostępem do koordynatora może uruchomić podgląd:

```bash
gh workflow run org-metadata-sync.yml --repo semcod/.github --ref main -f repository=autogrammar/toonic -f dry_run=true
```

Aby zapisać zmiany, użyj `dry_run=false`. Wynik jest widoczny w [uruchomieniach koordynatora](https://github.com/semcod/.github/actions/workflows/org-metadata-sync.yml).

<!-- docs:section limitations -->
## Ograniczenia

Aktualizacja odbywa się według harmonogramu, z możliwym opóźnieniem kolejki GitHub. Push do tego repozytorium nie uruchamia jej natychmiast. Dry-run sprawdza odczyt i proponowane wartości; skuteczny zapis wymaga udanego wykonania oraz kontroli API.

Dokument używa formatu wellmanifest/docs 0.1.1; nie deklaruje wdrożenia chronionego checkera dokumentacji.

<!-- docs:section next_actions -->
## Utrzymanie

Po zmianie właściciela repozytorium zaktualizuj katalog i konfigurację koordynatora, następnie sprawdź podgląd, wykonanie oraz wartości w API. Błędy synchronizacji diagnozuj w centralnym workflow. Przy zmianie mechanizmu zwiększ wersję tego dokumentu.
