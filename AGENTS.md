# Repository Guidelines

## Project Structure & Module Organization
- `backend/app`: FastAPI service (`api` routes, `services/inference.py`, `schemas`, `models`); runtime files in `backend/data` (uploads/results/temp).
- `frontend/src`: Vue 3 + TypeScript (`pages`, `components`, `stores`, `api`, `utils/constants.ts`); UnoCSS config in `uno.config.ts`.
- `nnUNet-msgpu1.10`: MindSpore nnU-Net training/inference; environment bootstrap in `setup_paths.sh`.
- `gh-kits19/starter_code`: KiTS19 download/visualization; `nnUNet_data/` holds raw/preprocessed/results and stays untracked.
- Repo docs: `docs/`, `README.md`, `CLAUDE.md`.

## Build, Test, and Development Commands
- Paths: run `source nnUNet-msgpu1.10/setup_paths.sh` first (sets `nnUNet_raw_data_base`, `nnUNet_preprocessed`, `RESULTS_FOLDER`).
- Backend: `cd backend && pip install -r requirements.txt && python run.py` (prod) or `uvicorn app.main:app --reload --port 8000` (dev, docs at `/docs`, ping `/health`).
- Frontend: `cd frontend && pnpm install && pnpm dev` (local) or `pnpm build` (type-check + bundle).
- nnU-Net: `cd nnUNet-msgpu1.10 && python eval.py -i <input_dir> -o <output_dir> -t Task001_kits -m 3d_fullres --disable_tta`; training: `python train.py 3d_fullres nnUNetTrainerV2 Task001_kits <fold>`.

## Coding Style & Naming Conventions
- Python: PEP8, 4 spaces, type hints for public functions, snake_case modules/functions, PascalCase classes; keep schemas/models aligned and keep paths inside `backend/data` read via `core/config.py`.
- TypeScript/Vue: `<script setup>` + Composition API, PascalCase components/pages (`HomePage.vue`), Pinia store ids as nouns (`viewer`, `inference`), typed API clients in `src/api/*.ts`, shared constants in `utils/constants.ts`; use `async/await` with typed Axios responses.
- Config stays in `.env` (`MODEL_PATH`, nnU-Net paths); never hardcode secrets or dataset locations.

## Testing Guidelines
- No formal suite yet; add backend tests with `pytest` (`backend/tests/test_*.py`), mock nnU-Net calls, and isolate file I/O with temp dirs. Smoke-check `/health` and a sample upload/inference run when touching backend flow.
- Frontend sanity: `pnpm build` for type errors; if adding specs, use `*.spec.ts` with Vitest and stub network calls. Note manual checks in PRs until automation improves.

## Commit & Pull Request Guidelines
- Use Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, `test:`, `build:`) with optional scopes (`backend`, `frontend`, `nnunet`).
- PRs should include a short summary, linked issue/task, commands run (`pnpm build`, backend start, inference check), any env/config changes, and screenshots/GIFs for UI tweaks. Keep data, weights, and `.env` out of git.

## Security & Configuration Tips
- Keep patient data and `nnUNet_data` artifacts outside version control; confirm `.gitignore` before committing.
- Target CUDA 11.6 + cuDNN 8.4.1 + MindSpore GPU 1.10; prefer single worker to avoid MindSpore process issues.
- Re-source `setup_paths.sh` in new shells and verify with `echo $nnUNet_raw_data_base` before training or inference.
