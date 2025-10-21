# GPU Setup for Local Models using UV

This document provides a guide on how to set up GPU support for local models while using UV dependency manager.
This setup is essential for leveraging the computational power of GPUs while using local models in the application.

UV provides a guide for setting up GPU support for local models, which can be found in [uv-pytorch-setup](https://docs.astral.sh/uv/guides/integration/pytorch/).

## Prerequisites

- Ensure you have a compatible GPU installed on your machine.
- Run the below command in your terminal to check if your GPU is recognized:

  ```bash
  nvidia-smi
  ```

  Note down the CUDA version displayed in the output, as it will be needed for the next steps.

## Setup

1. Add the below lines to your `pyproject.toml` file to include the necessary dependencies for GPU support:

   ```toml
   dependencies = [
       "torch>=2.8.0",
       "torchvision>=0.23.0",
   ]

   [tool.uv.sources]
   torch = { index = "pytorch-cu129" }
   torchvision = { index = "pytorch-cu129" }

   [[tool.uv.index]]
   name = "pytorch-cu129"
   url = "https://download.pytorch.org/whl/cu129"
   explicit = true
   ```

   Use the appropriate CUDA version in the URL based on your GPU's CUDA version.
   The package versions mentioned above are the latest available as of October 5, 2025.

2. Install the dependencies using UV:

   ```bash
   uv sync
   ```

   Remove existing lock file and .venv to ensure a clean installation.

3. Run the following command to verify that PyTorch is using the GPU:

   ```python
   python -c "import torch; print(torch.__version__); print(torch.cuda.is_available())"
   ```

   The output pytorch version should have a suffix like `+cu129` indicating CUDA 12.9 support, and
   `torch.cuda.is_available()` should return `True`.
