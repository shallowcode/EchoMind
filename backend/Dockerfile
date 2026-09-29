FROM golang:1.27.1-bookworm AS build
WORKDIR /src
COPY backend/go.mod backend/go.sum ./
RUN go mod download
COPY backend/ ./
RUN CGO_ENABLED=0 go build -trimpath -ldflags="-s -w" -o /out/supportflow ./cmd/server

FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates curl && rm -rf /var/lib/apt/lists/* && useradd -m -u 1000 supportflow
WORKDIR /app
COPY --from=build /out/supportflow /app/supportflow
COPY --chown=supportflow:supportflow frontend/ /app/frontend/
RUN mkdir /app/data && chown supportflow:supportflow /app/data
USER supportflow
EXPOSE 8002
HEALTHCHECK --interval=15s --timeout=4s --start-period=30s CMD curl -fsS http://127.0.0.1:8002/health || exit 1
CMD ["/app/supportflow", "-addr", "0.0.0.0:8002"]
