# Partitioning of urban networks to optimize postal delivery routes

This is the repository used for our Introduction to network analysis course at UL-FRI. 

Deploy of our project is available at: [https://delivery-sys-opt.herokuapp.com/](https://delivery-sys-opt.herokuapp.com/)

Project report is available at: [report.pdf](report.pdf)

## Structure

The repository contains multiple subfolders:
* `cache/` - the cache folder contains cached files for multiple procedures to increase 
interactivity of the interactive dashboard. 
* `data/` - the data folder contains all the datasets in `.csv` and Pajek format. 
* `util/` - the lib folder contains helper functions and classes. It is additionally broken down to:
    * `dash/` - the dashboard folder contains helper functions for the interactive dashboard. Here, we also specify all the tabs and how they function.
    * `lib/` - the lib folder contains the general helper methods and classes.
* `notebooks/` - the notebooks folder contains all the Jupyter notebooks used for data exploration and initial analyses.
* `scripts/` - the scripts folder contains all the Python scripts used for data exploration and initial analyses.
* `assets/` - the assets folder contains assets used in the interactive dashboard.

## Documentation
In `docs` you will find a more comprehensive documentation of our project:
* generation of graphs: [Graph generation](./docs/GraphGeneration.md)
* running scripts for graph partitioning: [Graph partitioning](./docs/GraphPartitioning.md)

## Environment setup
To setup the environment for this project, follow these instructions:

1. Install [Python version 3.8 or higher](https://www.python.org/downloads/) and [Anaconda](https://www.anaconda.com/products/individual).
2. Assuming you have `git` already installed, clone this repository to the desired destination:
    ```shell script
    git clone https://github.com/lzontar/Partitioning-of-urban-networks-to-optimize-postal-delivery-routes.git
    ```
3. Move to the folder, where you cloned this repository and import the environment from the config file using `pip` or `conda`:
    ```shell script
    # Anaconda environment
    conda env create --file environment.yml
   
    # pip environment
    pip install -r requirements-local.txt
    ```
4. If using Anaconda, activate environment: 
    ```shell script
    conda activate Projekt
    ```
5. To try out our interactive dashboard in root of the project execute:
    ```
    python Dashboard.py 
    ```
    Open your browser at [http://127.0.0.1:3010/](http://127.0.0.1:3010/) to access the interactive dashboard.

6. Explore the repository by yourself or use our documentation for better understanding.
