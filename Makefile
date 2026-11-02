.PHONY: check test model reconcile packet report
check:      ## gate 0 on everything
	python -m pipeline.validate
test:
	python -m pytest -q
model:      ## re-run the national model and compare with the registry
	python -m pipeline.check_model
reconcile:
	python -m pipeline.reconcile
packet:     ## is a research cycle due?
	python -m pipeline.research_packet --check
report:     ## build PDFs for the latest version: make report V=v1.0
	python -m pipeline.build_report $(V) --images
