# GitFlow — Foxcape

Branch model for [foxcape](https://github.com/andreferraro/foxcape).

## Branches

| Branch | Lifetime | Merge from | Merge to |
|--------|----------|------------|----------|
| `develop` | permanent | `feature/*`, `release/*` | — (default) |
| `main` | permanent | `release/*`, hotfix | — |
| `feature/*` | temporary | — | `develop` |
| `release/*` | temporary | `develop` | `main` + `develop` |
| `hotfix/*` | temporary | `main` | `main` + `develop` |

## Workflow

### Feature

```bash
git checkout develop
git pull origin develop
git checkout -b feature/my-feature
# ... commits ...
git push -u origin feature/my-feature
# open PR → develop
```

### Release (e.g. v0.1.0)

```bash
git checkout develop
git checkout -b release/v0.1.0
# bump version, changelog, final fixes
git checkout main && git merge --no-ff release/v0.1.0
git tag v0.1.0
git checkout develop && git merge --no-ff release/v0.1.0
git push origin main develop --tags
```

### Hotfix

```bash
git checkout main
git checkout -b hotfix/critical-fix
# fix
git checkout main && git merge --no-ff hotfix/critical-fix
git tag v0.1.1
git checkout develop && git merge --no-ff hotfix/critical-fix
git push origin main develop --tags
```

## GitHub settings

- **Default branch:** `develop`
- **PR base:** `develop` (features) or `main` (releases/hotfixes)
- **Protected branches:** enable required checks (`CI`) on `develop` and `main` before first release
