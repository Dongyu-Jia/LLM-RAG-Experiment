Currently the initial fine-tuning process is set up and experimented in EC2 instance named **`i-0cec5075e93e9ec75 (cs230FT)`** at **`us-west-2`** region. The instance is launched with `**Deep Learning Base OSS Nvidia Driver GPU AMI (Ubuntu 22.04) 20241023`** AMI with **`g4dn.2xlarge`** instance type (Tesla T4 GPU). 

Below are some commands for reference and used if needed:

     # stay up-to-date
     sudo apt update && sudo apt upgrade -y
     # display detailed information about your NVIDIA GPU
     nvidia-smi
     # ensure the installed nvidia driver match the recommended one from
     ubuntu-drivers devices
     
Below are the list of packages installed within my CUDA environment for reference:

    accelerate               1.0.1
    aiohappyeyeballs         2.4.3
    aiohttp                  3.10.10
    aiosignal                1.3.1
    anaconda-anon-usage      0.4.4
    archspec                 0.2.3
    asttokens                2.4.1
    attrs                    24.2.0
    beautifulsoup4           4.12.3
    bitsandbytes             0.44.1
    boltons                  23.0.0
    Brotli                   1.0.9
    certifi                  2024.8.30
    cffi                     1.17.1
    charset-normalizer       3.3.2
    comm                     0.2.2
    conda                    24.9.2
    conda-content-trust      0.2.0
    conda-libmamba-solver    24.9.0
    conda-package-handling   2.3.0
    conda_package_streaming  0.10.0
    cryptography             43.0.0
    datasets                 3.0.2
    debugpy                  1.8.7
    decorator                5.1.1
    dill                     0.3.8
    distro                   1.9.0
    docstring_parser         0.16
    exceptiongroup           1.2.2
    executing                2.1.0
    filelock                 3.13.1
    frozendict               2.4.2
    frozenlist               1.5.0
    fsspec                   2024.2.0
    hf_transfer              0.1.8
    huggingface-hub          0.26.1
    idna                     3.7
    importlib_metadata       8.5.0
    ipykernel                6.29.5
    ipython                  8.29.0
    jedi                     0.19.1
    Jinja2                   3.1.3
    jsonpatch                1.33
    jsonpointer              2.1
    jupyter_client           8.6.3
    jupyter_core             5.7.2
    libmambapy               1.5.8
    lxml                     5.3.0
    markdown-it-py           3.0.0
    MarkupSafe               2.1.5
    matplotlib-inline        0.1.7
    mdurl                    0.1.2
    menuinst                 2.1.2
    mkl_fft                  1.3.10
    mkl_random               1.2.7
    mkl-service              2.4.0
    mpmath                   1.3.0
    multidict                6.1.0
    multiprocess             0.70.16
    nest_asyncio             1.6.0
    networkx                 3.4.2
    numpy                    2.1.2
    nvidia-cublas-cu12       12.4.5.8
    nvidia-cuda-cupti-cu12   12.4.127
    nvidia-cuda-nvrtc-cu12   12.4.127
    nvidia-cuda-runtime-cu12 12.4.127
    nvidia-cudnn-cu12        9.1.0.70
    nvidia-cufft-cu12        11.2.1.3
    nvidia-curand-cu12       10.3.5.147
    nvidia-cusolver-cu12     11.6.1.9
    nvidia-cusparse-cu12     12.3.1.170
    nvidia-nccl-cu12         2.21.5
    nvidia-nvjitlink-cu12    12.4.127
    nvidia-nvtx-cu12         12.4.127
    packaging                24.1
    pandas                   2.2.3
    parso                    0.8.4
    peft                     0.13.2
    pexpect                  4.9.0
    pgvector                 0.3.6
    pickleshare              0.7.5
    pillow                   10.4.0
    pip                      24.2
    platformdirs             3.10.0
    pluggy                   1.0.0
    prompt_toolkit           3.0.48
    propcache                0.2.0
    protobuf                 3.20.3
    psutil                   6.1.0
    psycopg2-binary          2.9.10
    ptyprocess               0.7.0
    pure_eval                0.2.3
    pyarrow                  17.0.0
    pycosat                  0.6.6
    pycparser                2.21
    Pygments                 2.18.0
    PySocks                  1.7.1
    python-dateutil          2.9.0
    pytz                     2024.2
    PyYAML                   6.0.2
    pyzmq                    25.1.2
    regex                    2024.9.11
    requests                 2.32.3
    rich                     13.9.3
    ruamel.yaml              0.18.6
    ruamel.yaml.clib         0.2.8
    safetensors              0.4.5
    sentencepiece            0.2.0
    setuptools               70.0.0
    shtab                    1.7.1
    six                      1.16.0
    soupsieve                2.6
    stack-data               0.6.2
    sympy                    1.13.1
    tokenizers               0.20.1
    torch                    2.5.1
    torchaudio               2.5.1
    torchvision              0.20.1
    tornado                  6.4.1
    tqdm                     4.66.5
    traitlets                5.14.3
    transformers             4.46.0
    triton                   3.1.0
    trl                      0.11.1
    truststore               0.8.0
    typing_extensions        4.9.0
    tyro                     0.8.14
    tzdata                   2024.2
    unsloth                  2024.10.7
    unsloth_zoo              2024.10.5
    urllib3                  2.2.3
    wcwidth                  0.2.13
    wheel                    0.44.0
    xformers                 0.0.28.post2
    xxhash                   3.5.0
    yarl                     1.16.0
    zipp                     3.20.2
    zstandard                0.23.0