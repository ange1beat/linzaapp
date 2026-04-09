#!/usr/bin/env bash
# Creates 25 custom labels for Linza Detector task tracking.
# Usage: ./setup-labels.sh <owner/repo>
# Requires: gh CLI authenticated (gh auth login)

set -euo pipefail

REPO="${1:?Usage: setup-labels.sh owner/repo}"

declare -A LABELS=(
  # Type
  ["type: bug"]="d73a4a:Баг"
  ["type: feature"]="0075ca:Новая функциональность"
  ["type: enhancement"]="a2eeef:Улучшение существующего"
  ["type: docs"]="0e8a16:Документация"
  ["type: refactor"]="d4c5f9:Рефакторинг"
  ["type: devops"]="f9d0c4:CI/CD, инфраструктура"
  ["type: test"]="bfd4f2:Тестирование"
  # Priority
  ["priority: critical"]="b60205:Блокирующий, срочно"
  ["priority: high"]="d93f0b:Важный"
  ["priority: medium"]="fbca04:Обычный приоритет"
  ["priority: low"]="0e8a16:Может подождать"
  # Stage
  ["stage: planning"]="c2e0c6:Проработка плана"
  ["stage: in-progress"]="1d76db:В работе"
  ["stage: review"]="5319e7:На ревью"
  ["stage: testing"]="f9d0c4:Тестирование/QA"
  ["stage: blocked"]="e4e669:Заблокировано"
  # Scope
  ["scope: frontend"]="7057ff:Фронтенд"
  ["scope: backend"]="008672:Бэкенд"
  ["scope: infra"]="e36209:Инфраструктура"
  # Service
  ["service: board"]="0A6FFF:linza-board"
  ["service: storage"]="14B8A6:linza-storage-service"
  ["service: analytics"]="F87171:linza-analytics"
  ["service: vpleer"]="FBBF24:linza-vpleer"
  ["service: debug"]="34D399:linza-debug"
  ["service: deploy"]="94A3B8:linza-deploy"
  ["service: cross-repo"]="c5def5:Затрагивает несколько сервисов"
)

echo "Creating labels for $REPO..."
for label in "${!LABELS[@]}"; do
  IFS=':' read -r color desc <<< "${LABELS[$label]}"
  gh label create "$label" --repo "$REPO" --color "$color" --description "$desc" --force 2>/dev/null && \
    echo "  ✓ $label" || echo "  ✗ $label (failed)"
done
echo "Done! Created 25 labels for $REPO"
