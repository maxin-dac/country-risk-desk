# Changelog

Tous les changements notables de ce projet seront documentés dans ce fichier.

Le format est basé sur [Conventional Changelog](https://github.com/conventional-changelog/conventional-changelog)
et le projet adhère au [Versionnage Sémantique](https://semver.org/lang/fr/).

> Généré automatiquement par le workflow de versioning (`.github/workflows/versioning.yml`)
> lors de chaque push sur `main`. Aucune édition manuelle nécessaire.

---

## [0.1.0] - 2026-09-08

### ✨ Nouveautés

- Mise en place du versioning automatique basé sur **Conventional Commits**
- Affichage de la version dans le footer du dashboard Streamlit
- Génération automatique du CHANGELOG et des GitHub Releases
- Intégration avec le refresh mensuel de données

### 📚 Documentation

- Configuration `.versionrc` pour les types de commits
- Configuration `.commitlintrc.js` pour la validation des messages de commit

---

## Types de commits reconnus

| Préfixe    | Section CHANGELOG      | Impact version |
|------------|------------------------|----------------|
| `feat!`    | ✨ Nouveautés (BREAKING) | MAJOR          |
| `feat`     | ✨ Nouveautés          | MINOR          |
| `fix`      | 🐛 Corrections         | PATCH          |
| `perf`     | ⚡ Performances        | PATCH          |
| `refactor` | ♻️ Refactoring         | PATCH          |
| `data`     | 📊 Données             | PATCH          |
| `docs`     | 📚 Documentation       | —              |
| `test`     | 🧪 Tests               | —              |
| `ci`       | 🔧 CI/CD               | —              |
| `build`    | 🏗️ Build               | —              |
