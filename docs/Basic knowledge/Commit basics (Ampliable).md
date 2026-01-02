### Básico del día a día
- `git status`
- `git pull`
- `git add .`
- `git commit -m "mensaje"`
- `git push`
- `git submodule update --init --recursive` Este actualiza todos los submódulos

	### Ver cambios e historial
- `git diff`
- `git diff --staged`
- `git log --oneline --decorate --graph --all`

### Ramas (flujo habitual)
- `git branch`
- `git switch -c nueva_rama` *(o `git checkout -b 17.0-nueva_rama`)*
- `git switch otra_rama` *(o `git checkout 17.0-otra_rama`)*
- `git fetch --all --prune`

### Merge / Rebase (muy usado en mi flujo)
- `git merge nueva_rama`
- `git rebase -i HEAD~5`
- `git push origin rama_subida --force

### Deshacer / Reset
- `git reset --soft HEAD~1` *(deshace commit, deja staged)*
- `git reset --hard HEAD` *(OJO: descarta cambios locales)*

### Borrar ramas
- `git branch -d 17.0-rama` *(borrar local si está mergeada)*
- `git branch -D 17.0-rama` *(borrar local forzado)*
- `git push origin --delete 17.0-rama` *(borrar remota)*

### Opcional: borrar todas las ramas remotas excepto `main`/`master` (ajusta si hace falta)
- `git branch -r | grep -vE 'origin/(main|master)$' | sed 's|origin/||' | xargs -n 1 git push origin --delete`