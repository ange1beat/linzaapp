up:
	docker compose up -d

shell-ui:
	docker compose exec lm-ui ash

install-ui:
	docker compose exec lm-ui yarn install --frozen-lockfile

run-ui:
	docker compose exec lm-ui yarn run dev

run-storybook:
	docker compose exec lm-ui yarn run storybook

test-ui:
	docker compose exec lm-ui yarn run test

down:
	docker compose down

run-build:
	docker compose exec lm-ui yarn run build

lint:
	docker compose exec lm-ui yarn run lint

compile-emails:
	docker build -f emails/Dockerfile -t lm-emails:latest .
	docker run -it --name lm-emails --volume ./emails:/app --rm lm-emails:latest
