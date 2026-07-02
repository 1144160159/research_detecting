# FedScope 

This repository contains the code of:<b> FedScope – Federated Host Embeddings from Telescope Traffic: Design and Implementation</b>


## Install

1. Clone this repository
2. Create and activate a virtual environment (recommended):

```bash
cd fedscope
python -m venv ./.venv
source ./.venv/bin/activate
```

3. Install Python dependencies:

```bash
pip install -r requirements.txt
```

5 Manual replacement of the original  <i>flwr</i> library with  the one modified:

```bash
rm -r ./.venv/lib/[PYTHON_VERSION]/site-packages/flwr
mv -r ./flwr ./.venv/lib/[PYTHON_VERSION]/site-packages
```
## Run as container

This project can be run inside Docker containers (server + one or more clients). Below are minimal steps to build the images and run them locally.

### Prerequisites

- Docker (and optionally Docker Compose / `docker compose` plugin)
- Linux is required for `network_mode: host` in the provided compose file

###  Build images

1.  Build the base image (it contains the library used by client and server):

```bash
docker build -f docker/base.Dockerfile -t fedscope_base_image:latest .
```

2. Build server and client images:

```bash
docker build -f docker/server.Dockerfile -t fedscope_server:latest .
docker build -f docker/client.Dockerfile -t fedscope_client:latest .
```

> Tip: If you intend to push images to a registry, tag them as `<NAME>/fedscope_server:latest` and `<NAME>/fedscope_client:latest` before pushing.



### Docker Compose

The compose file at `docker/compose.yaml` references images like `<NAME>/fedscope_server:latest`. Either replace `<NAME>/` with your registry/username or remove it to use the locally-built images.
Then start containers:

```bash
docker compose -f docker/compose.yaml up
```

### Dataset

Our dataset is available upon request, please contact the authors to get access
