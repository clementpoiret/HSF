# Installation

HSF is thought to be easily installable.

However, as it can be used with several different hardware acceleration platforms,
some of the installation steps may vary.


## Setting up a new environment

We encourage you to use the [`conda`](https://conda.io/) environment manager
to use HSF.

To create a new environment, run the following commant:

`conda create -n hsf python=3.9`

Then, activate the new environment:

`source activate hsf`


## Installation from PyPI

You'll be able to to install HSF from PyPI by following the instructions:

=== "CPU"

    ```shell
    pip install hsf
    ```

=== "CUDA"

    First of all, please have a working [`CUDA`](https://developer.nvidia.com/cuda-toolkit)
    and [`cuDNN`](https://developer.nvidia.com/cudnn) installation.

    - The path to the CUDA installation must be provided via the `CUDA_PATH` environment variable,
    - The path to the cuDNN installation (include the cuda folder in the path) must be provided via the `cuDNN_PATH` environment variable. The cuDNN path should contain bin, include and lib directories.
    - The path to the cuDNN bin directory must be added to the PATH environment variable.

    ONNXRuntime 1.8 requires at least CUDA 11.0.3, and cuDNN 8.0.4. For newer versions, please
    check the [ONNXRuntime documentation](https://onnxruntime.ai/docs/execution-providers/CUDA-ExecutionProvider.html)

    Then run the following commands:

    ```shell
    pip install hsf
    pip install onnxruntime-gpu
    ```

=== "DirectML"

    DirectML is compatible with Windows 10, version 1709 (10.0.16299; RS3, “Fall Creators Update”) and newer.

    ```shell
    pip install hsf
    pip install onnxruntime-directml
    ```

    See [the ONNXRuntime documentation](https://onnxruntime.ai/docs/execution-providers/DirectML-ExecutionProvider.html) or
    [the Microsoft documentation](https://docs.microsoft.com/en-us/windows/ai/directml/dml) for more details.

=== "Other Execution Providers"

    Please refer to [the ONNXRuntime documentation](https://onnxruntime.ai/docs/build/eps.html).

You can now check the installation and default parameters of HSF using `hsf -h`.


## Installation from sources

HSF is using Poetry to manage its dependencies. To install HSF from sources,
be sure to have a working [Poetry installation](https://python-poetry.org/docs/#installation).

Then, run:

```shell
git clone git@github.com:clementpoiret/HSF.git
cd HSF
poetry install
```

Taken from the [Poetry documentation](https://python-poetry.org/docs/basic-usage/#using-your-virtual-environment), poetry creates a virtual environment in `{cache-dir}/virtualenvs`. You can change the cache-dir value by editing the poetry config. Additionally, you can use the virtualenvs.in-project configuration variable to create virtual environment within your project directory.

To use HSF, activate the environment created by Poetry by doing `source {path_to_venv}/bin/activate`.
