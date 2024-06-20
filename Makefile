download_model:
	chmod +x ./scripts/download_models.sh
	./scripts/download_models.sh

config:
	mkdir -p logs && touch logs/celery.log
	cp configs/env.example configs/.env
	# And add params ...

# Docker
build:
	docker build -t ai-talking-face -f Dockerfile .

start:
	docker compose -f docker-compose.yml down
	docker compose -f docker-compose.yml up -d

start-prod:
	docker compose -f docker-compose-prod.yml down
	docker compose -f docker-compose-prod.yml up -d

stop:
	docker compose -f docker-compose.yml down

stop-prod:
	docker compose -f docker-compose-prod.yml down

# Checker
cmd-image:
	docker run -it --gpus all --rm ai-talking-face /bin/bash

cmd-worker:
	docker compose exec worker-ai-talking-face /bin/bash

log-worker:
	cat logs/celery.log

# check:
#	printenv LD_LIBRARY_PATH
#	python
# 	import torch
#	print(torch.cuda.is_available())
# 	print(torch.__version__)
# 	print(torch.version.cuda)
# 	print(torch.backends.cudnn.version())
#	python inference.py --driven_audio ./examples/voice.wav --source_image ./examples/do_mixi.jpg --enhancer gfpgan
