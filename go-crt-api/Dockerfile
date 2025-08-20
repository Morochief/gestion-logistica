# Dev-oriented Dockerfile for go-crt-api (HTTP :8080)
# Use Go toolchain >= 1.24 to satisfy module requirement

FROM golang:1.24-alpine

WORKDIR /src

# Faster builds: cache modules
COPY go.mod go.sum ./
RUN go mod download

# Copy the rest only for initial image; compose will bind-mount later
COPY . .

# Expose API port
EXPOSE 8080

# Default dev command; compose may override
CMD ["go", "run", "./main.go"]