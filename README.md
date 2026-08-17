## trex_toy
This repository provides a proof of concept implementation of the succinct graph representation scheme TREX, introduced in "Rooting Out Entropy: Optimal Tree Extraction for Ultra-Succinct Graphs" by Alaoui et al. 
TREX allows for storing a directed or undirected graph compactly, while still being able to support navigational queries directly on the succinct representation.

This repository accompanies my bachelor's thesis "Empirical Evaluation of Tree Extraction", which can be viewed as `thesis.pdf` for any further information on this project. This README only covers brief information on how to run the code. 

## Setup
```bash
git clone https://github.com/Laserjullu/trex_toy
pip install networkx numpy pandas tqdm scikit-learn statsmodels
cd trex_toy
```
Now one can evaluate graphs theoretical TREX compression and many different figures from within this environment, the graphs must be stored as edgelists (`source target`):

```bash
python -m evaluation.pipeline path/to/edgelist/directory [--undirected] [--output results.csv]
```
Where `--undirected` must be applied for undirected graphs and `--output` can be specified, if the csv file containing the results (apart from the print statements) should not be stored as `trex_results.csv` within the working directory (`trex_toy`). 

## Reproducing the Thesis Results
All the figures — except the data from the regression — used in the thesis are displayed in `results.csv`. To replicate most, the pipeline must be run once on each of the (unzipped) five dataset categories (or twice, if broader categorized by directed/undirected). To additionally get the figures for the different tree extraction strategies, a further run with the `--antiGreedy` and `--random` flags set, is necessary. The figures for the regression can be computed by executing `model.py`, which includes the once manually entered data-points for the regression. 

Finally, many of the figures in the thesis are simple deviations of numbers computed by `pipeline.py`. Therefore, to preserve clarity, some of the original figures are omitted in the CSV, and only the final ones are displayed.

## Testing
To validate each of the TREX queries against NetworkX ground truth on 2000 random graphs plus a few manual edge cases, run: 
```bash
python -m unittest Tests.test_automated
```


