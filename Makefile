start-server:
	uvicorn server:app --reload --port 8000

ngrok:
	ngrok http 8000

test-wapp-api:
	curl -X POST http://localhost:8000/webhook -H "Content-Type: application/json" -d '{"message": "Hello, world!"}'

test-time-extractor-agent:
	python -m agents.time_extractor

test-location-detector-agent:
	python -m agents.location_detector

test-booking-utils:
	python -m utils.booking_utils

