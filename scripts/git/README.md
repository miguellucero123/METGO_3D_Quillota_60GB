# Scripts manuales — subir a GitHub

**Repositorio:** https://github.com/miguellucero123/METGO_3D_Quillota_60GB.git  
**Rama habitual:** `master`

Ejecute los pasos **en orden**. Usted confirma cada commit (no hay push automático sin su mensaje).

| Paso | Script | Qué hace |
|------|--------|----------|
| 0 | `00_abrir_terminal_aqui.bat` | `cd` al repo |
| 1 | `01_revisar_estado.bat` | `status`, remoto, últimos commits |
| 2 | `02_preparar_staging.bat` | `git add -A` + quita secretos/caché del staging |
| 3 | `03_commit_manual.bat` | Pide mensaje y hace `git commit` |
| 4 | `04_push_master.bat` | `git push origin master` |
| — | `SUBIR_GITHUB_MENU.bat` | Menú con todos los pasos |
| — | `subir_github_manual.ps1` | Misma guía en PowerShell |
| — | `COMANDOS_GIT_MANUAL.txt` | Comandos para copiar/pegar |

**Guía detallada:** [`docs/manuales/SUBIR_GITHUB_MANUAL.md`](../../docs/manuales/SUBIR_GITHUB_MANUAL.md)

**No subir nunca:** `.env`, `secrets.toml`, contraseñas, `datos_runtime/`, bases `.db` locales.
