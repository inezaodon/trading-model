.PHONY: demo smoke install-api

install-api:
	python3 -m pip install -r apps/api/requirements.txt

demo:
	./scripts/run-demo.sh

smoke:
	./scripts/smoke-api.sh
