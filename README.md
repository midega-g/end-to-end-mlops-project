# End to End MLOps Project

A project that starts from data preprocessing to the monitoring of the deployed model(s). A detailed breakdown of what is entailed in this data can be found in this [post](https://medium.com/@midegageorge2/predictive-model-development-maximizing-ifoods-marketing-campaign-profitability-by-targeting-95fe1ae79478). However, in this project, the data has been split into four parts which may lead to the difference in results observed in the article. There is a notebook detailing how the four datasets were created in the `data` folder.

## Environment Preparation

The following installations will be based on your operating system. Just click the link to visit the official documentation page on how to install them.

1. [Anaconda](https://docs.anaconda.com/anaconda/install/)
2. [Docker Engine](https://docs.docker.com/engine/install/)
3. (Optional if running on Ubuntu distribution)[Docker Compose](https://docs.docker.com/compose/install/)
4. (Optional) Ubuntu distribution

Create, activate, and deactivate a conda environment with Python version 3.9.16. Make sure to run the commands one at a time

```bash
conda create -n ifood_mlops python=3.9.16
conda activate ifood_mlops
conda deactivate
```
Install the required packages

```bash
pip install -r requirements.txt
```









