FROM node:20-alpine

WORKDIR /app

RUN yarn global add nodejs mjml

ENTRYPOINT ["mjml", "/app/*.mjml", "--config.minify", "-o", "/app/output"]
