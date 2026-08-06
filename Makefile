PYTHON ?= python3
RUFF   ?= ruff

.PHONY: check lint validate parity benchmark-digests privacy-scan grade-evals test docs media release-check all

# `check` runs what CI runs. It previously ran only check_all.py while CI also
# ran ruff, so a green local gate said nothing about whether CI would pass —
# and the first push failed on three lint errors that had never been visible
# locally. If the two ever diverge again, that is the bug.
check: lint
	$(PYTHON) scripts/check_all.py

# A missing linter is a blocker, not a pass. Skipping it silently would restore
# exactly the gap this target exists to close, so it fails with instructions.
lint:
	@command -v $(RUFF) >/dev/null 2>&1 || { \
		echo "FAILED: ruff is not installed, so the lint gate cannot run."; \
		echo "  It is pinned in requirements.lock and CI runs it on every push."; \
		echo "  Install it:  $(PYTHON) -m pip install --requirement requirements.lock"; \
		exit 1; \
	}
	$(RUFF) check scripts tests

validate:
	$(PYTHON) scripts/validate_repo.py

parity:
	$(PYTHON) scripts/check_docx_parity.py

benchmark-digests:
	$(PYTHON) scripts/verify_benchmark_digests.py

privacy-scan:
	$(PYTHON) scripts/privacy_scan.py

grade-evals:
	$(PYTHON) scripts/grade_local_evals.py

test:
	$(PYTHON) -m unittest discover -s tests -v

# One starter per released package. The previous recipe built a single
# `starter/ClinPharm-AI-Start.md` that no longer exists — a leftover from when
# the repository held one skill — so this target could not complete.
docs:
	$(PYTHON) scripts/build_docx.py starter/build-work-context/Pharma-Work-Context.md starter/build-work-context/Pharma-Work-Context.docx
	$(PYTHON) scripts/build_docx.py starter/review-csr-pk-consistency/CSR-PK-Consistency-Review.md starter/review-csr-pk-consistency/CSR-PK-Consistency-Review.docx
	$(PYTHON) scripts/build_docx.py examples/clinpharm-pmx/outputs/My-Pharma-Work-Context.md examples/clinpharm-pmx/outputs/My-Pharma-Work-Context.docx
	$(PYTHON) scripts/build_docx.py examples/clinpharm-pmx/outputs/AI-Working-Pack-SYN-101.md examples/clinpharm-pmx/outputs/AI-Working-Pack-SYN-101.docx

media:
	$(PYTHON) scripts/build_demo_gif.py
	swift scripts/build_demo_mp4.swift docs/assets/demo docs/assets/clinpharm-ai-workflow.mp4

release-check: check
	$(PYTHON) scripts/build_release.py --check

all: docs media check
