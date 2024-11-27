#!/bin/bash

# Function to detect OS and architecture
detect_architecture() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        OS="Mac"
        ARCH=$(uname -m)
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="Linux"
        ARCH=$(uname -m)
    else
        echo "Unsupported OS."
        exit 1
    fi
}

# Check if Miniconda is already installed
if [ -d "$HOME/miniconda" ]; then
    echo "Miniconda is already installed."
else
    detect_architecture
    
    # Define Miniconda installation URL and installer script name
    if [ "$OS" == "Mac" ]; then
        if [ "$ARCH" == "arm64" ]; then
            MINICONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh"
            INSTALLER_SCRIPT="Miniconda3-latest-MacOSX-arm64.sh"
        else
            MINICONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh"
            INSTALLER_SCRIPT="Miniconda3-latest-MacOSX-x86_64.sh"
        fi
    elif [ "$OS" == "Linux" ]; then
        MINICONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"
        INSTALLER_SCRIPT="Miniconda3-latest-Linux-x86_64.sh"
    fi

    # Download the Miniconda installer script
    echo "Downloading Miniconda installer for $OS ($ARCH)..."
    wget $MINICONDA_URL -O $INSTALLER_SCRIPT

    # Verify the download
    if [ $? -ne 0 ]; then
        echo "Failed to download Miniconda installer."
        exit 1
    fi

    # Make the installer script executable
    chmod +x $INSTALLER_SCRIPT

    # Run the installer script
    echo "Running Miniconda installer..."
    ./$INSTALLER_SCRIPT -b -p $HOME/miniconda

    # Verify the installation
    if [ $? -ne 0 ]; then
        echo "Miniconda installation failed."
        exit 1
    fi

    # Initialize Miniconda
    echo "Initializing Miniconda..."
    $HOME/miniconda/bin/conda init

    # Clean up the installer script
    rm $INSTALLER_SCRIPT

    echo "Miniconda installation completed successfully."
fi

source ~/.bashrc  # Activate conda
$HOME/miniconda/bin/conda init bash

# Add conda forge channel to get latest packages
$HOME/miniconda/bin/conda config --add channels conda-forge

# Check if the 'rag' conda environment exists
if ! $HOME/miniconda/bin/conda env list | grep -q '^rag-simplify\s'; then
    # Create conda environment from env.yaml
    $HOME/miniconda/bin/conda env create -f setup/env-simplify.yaml
fi

$HOME/miniconda/bin/conda env update --file setup/env-simplify.yaml --name rag-simplify

$HOME/miniconda/bin/conda env export > setup/environment_snapshot_backup.yml  

$HOME/miniconda/bin/conda info --envs

echo "run 'conda activate rag' to activate the conda environment"

