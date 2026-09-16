#!/usr/bin/env bash
# Publish the all-in-one messaging-lab image to Docker Hub (or another registry).
set -euo pipefail

REGISTRY="${REGISTRY:-docker.io}"
NAMESPACE="${DOCKERHUB_USER:-${NAMESPACE:-}}"
IMAGE_NAME="${IMAGE_NAME:-messaging-lab}"
TAG="${TAG:-latest}"

if [[ -z "$NAMESPACE" ]]; then
  echo "Set DOCKERHUB_USER (or NAMESPACE) to your Docker Hub username/org."
  echo "Example: DOCKERHUB_USER=mycompany ./scripts/publish-all-in-one.sh"
  exit 1
fi

FULL_IMAGE="${REGISTRY}/${NAMESPACE}/${IMAGE_NAME}:${TAG}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "Building ${FULL_IMAGE} ..."
docker build -t "${FULL_IMAGE}" -t "${NAMESPACE}/${IMAGE_NAME}:${TAG}" \
  "${ROOT}/dockerfiles/all-in-one"

echo "Logging in to registry (if needed) ..."
if [[ "$REGISTRY" == "docker.io" ]]; then
  docker login
else
  docker login "$REGISTRY"
fi

echo "Pushing ${FULL_IMAGE} ..."
docker push "${FULL_IMAGE}"

echo
echo "Users can run:"
echo "  docker pull ${NAMESPACE}/${IMAGE_NAME}:${TAG}"
echo "  docker run --rm --name messaging-lab --shm-size=1g \\"
echo "    -p 6379:6379 -p 61616:61616 -p 61613:61613 -p 1883:1883 -p 5672:5672 -p 8161:8161 \\"
echo "    -p 5675:5675 -p 15672:15672 -p 9092:9092 -p 4222:4222 -p 8222:8222 \\"
echo "    -p 5000:5000 -p 8086:8086 \\"
echo "    ${NAMESPACE}/${IMAGE_NAME}:${TAG}"
echo
echo "See docs/USAGE_GUIDE.md for ports and test commands."
