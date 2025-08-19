# Multi-stage build for NetGrid Go
# Stage 1: Build the application
FROM golang:1.21-alpine AS builder

# Install build dependencies
RUN apk add --no-cache git ca-certificates tzdata

# Set working directory
WORKDIR /app

# Copy go mod file
COPY go.mod ./

# Copy the rest of the source code
COPY . .

# Download dependencies and generate go.sum
RUN go mod tidy

# Build the application
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o netgrid-go .

# Stage 2: Create minimal runtime image
FROM alpine:latest

# Install runtime dependencies
RUN apk --no-cache add ca-certificates tzdata iproute2

# Create non-root user
RUN addgroup -g 1001 -S netgrid && \
    adduser -u 1001 -S netgrid -G netgrid

# Set working directory
WORKDIR /app

# Copy binary from builder stage
COPY --from=builder /app/netgrid-go .

# Change ownership to non-root user
RUN chown netgrid:netgrid /app/netgrid-go

# Switch to non-root user
USER netgrid

# Set entrypoint
ENTRYPOINT ["./netgrid-go"]

# Default command (can be overridden)
CMD ["--help"] 