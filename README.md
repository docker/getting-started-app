
# Getting Started

This repository is a sample application for users following the [Getting Started guide](https://docs.docker.com/get-started/) on Docker's official documentation.

The application is based on the tutorial at [docker/getting-started](https://github.com/docker/getting-started).

## Getting Started App with Docker CI/CD

This project demonstrates how to build, test, and deploy a Dockerized application using GitHub Actions for CI/CD.

### How to Fork and Set Up

1. **Fork the repository:**
   - Go to the [docker/getting-started-app](https://github.com/docker/getting-started-app) and fork the repository to your GitHub account.

2. **Set the remote URL:**
   - After forking, change the remote URL to your repository in the terminal:
     ```bash
     git remote set-url origin https://github.com/abohmeed/getting-started-app.git
     ```

3. **View the Dockerfile:**
   - In the terminal, view the Dockerfile:
     ```bash
     cat Dockerfile
     ```

### Dockerfile

Here’s the `Dockerfile` included in this project:

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY . .
RUN yarn install --production && yarn cache clean
ENTRYPOINT [ "node" ]
CMD [ "src/index.js" ]
EXPOSE 3000
```

### GitHub Actions CI/CD Workflow

This project includes a GitHub Actions workflow for automatically building and pushing Docker images to the GitHub Container Registry.

#### Workflow File

The `.github/workflows/docker-image.yml` file contains the CI/CD pipeline:

```yaml
name: Docker Image CI

on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3

    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3

    - name: Log in to GitHub Container Registry
      uses: docker/login-action@v3
      with:
        registry: ghcr.io
        username: ${{ github.repository_owner }}
        password: ${{ secrets.GITHUB_TOKEN }}

    - name: Build and push Docker image
      uses: docker/build-push-action@v5
      with:
        context: .
        push: true
        tags: |
          ghcr.io/${{ github.repository_owner }}/abohmeed/getting-started:latest
          ghcr.io/${{ github.repository_owner }}/abohmeed/getting-started:${{ github.sha }}
```

### Workflow Steps:

- **Checkout code:** Fetches the repository content.
- **Set up Docker Buildx:** Prepares Docker Buildx for multi-platform builds.
- **Log in to GitHub Container Registry:** Authenticates the Docker client with GitHub’s Container Registry.
- **Build and push:** Builds the Docker image and pushes it to the GitHub Container Registry with two tags: `latest` and the commit SHA.

### Conclusion

This setup allows you to continuously integrate and deploy Docker images to the GitHub Container Registry. Simply push or open a pull request to the `main` branch, and the workflow will handle the rest!
