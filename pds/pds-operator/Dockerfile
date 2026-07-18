FROM node:22-alpine AS builder
WORKDIR /app

RUN apk add --no-cache git

ARG GIT_COMMITTER_NAME="Anhgelus Morhtuuzh"
ARG GIT_COMMITTER_EMAIL="me@anhgelus.world"

RUN git clone "https://tangled.org/brookie.blog/pds-operator" .
ADD *.patch .
RUN for p in $(ls *.patch); do git am < $p; done

RUN cd web && npm ci && npm run build
RUN cd server && npm ci && npm run build && npm prune --omit=dev

FROM node:22-alpine

ENV NODE_ENV=production

LABEL org.opencontainers.image.source="https://tangled.org/nouveauprintemps.org/infra" \
    org.opencontainers.image.description=" An easy to set up and operate PDS admin panel." \
    org.opencontainers.image.licenses=MIT \
    org.opencontainers.image.title="PDS Operator Repack" \
    org.opencontainers.image.version="1.0.0" \
    org.opencontainers.image.authors="Anhgelus Morhtuuzh" \
    io.atcr.readme="https://mirror.tangled.network/xrpc/sh.tangled.git.temp.getBlob?path=README.md&ref=main&repo=did%3Aplc%3Attxjyxhe6azr225um2t3t3v5" \
    io.atcr.icon="https://mirror.tangled.network/xrpc/sh.tangled.git.temp.getBlob?path=docs%2Fscreenshot-default.png&ref=main&repo=did%3Aplc%3Attxjyxhe6azr225um2t3t3v5"

WORKDIR /app/server

EXPOSE 8787

RUN mkdir /data

RUN apk add --no-cache dumb-init

ENTRYPOINT [ "dumb-init", "--" ]

COPY --from=builder /app/server/node_modules node_modules
COPY --from=builder /app/server/dist dist
COPY --from=builder /app/server/package.json package.json
COPY --from=builder /app/web/dist /app/web/dist

CMD [ "node", "dist/index.js" ]
