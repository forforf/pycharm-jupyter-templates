# Nbtplt

Notebook Templates for PyCharm Jupyter Notebooks.

Quick and dirty framework for creating extensible notebook templates. 
Put all your common cells into a notebook template and generate multiple files from that template.

## Installation

TBD: I use it locally. It **should** work with standard python setup, but I've not really tested it.

## Usage

### Working Example
There is a working example in the `./notebook` directory of this repo.
Just run the `nbtplt-maker.ipynb` notebook.

### Instructions

#### Source Notebooks

The source notebooks have the specific data we want to insert into the template.
Maybe it has the specific models we want to investigate

notebook: `logr.ipynb`
```python
# PyCharm uses `#%%` to delineate cells
# Identify the data to import into the template by assigning an id and type to the cell
# Example `#%% nbtplt my-id code` has an id of 'my-id' and indicates that the cell is a code cell.

#%% nbtplt concrete-model code
from sklearn.linear_model import LogisticRegression
model = LogisticRegression()

#%%
# A different cell, but this one will be ignored by the templating engine because it does not have
# a template id
```

notebook: `svr.ipynb`
```python
#%% nbtplt concrete-model code
from sklearn.svm import SVR
model = SVR()
```

### Template Notebook

The template notebook holds the common code and markdown that you will be reused.

notebook: `fitter-template.ipynb`
```python
# PyCharm uses `#%%` to delineate cells
# Identify the data to import into the template by assigning an id and type to the cell
# Example `#%% nbtplt my-id code` has an id of 'my-id' and indicates that the cell is a code cell.

#%% nbtplt concrete-model code
# This cell will be replaced by cell with id of `concrete-model` from the source notebook

#%%
model.fit(X, y)

# Do more things with model
```

### Template Generator

The template generator is what glues the sources and templates together to generate the templated notebook.

notebook: `generate-from-template.ipynb`
```python
# Regular python code call it from a cell or from a python program
from nbtplt.core import NbTpltChain

# Usage
# nbchain = NbtpltChain(generated_doc_path_prefix, template_nb_path, source_nb_paths)
# nbchain.generate() # to create templated notebook
#
# Or you can do it without interim variables
# NbtpltChain(generated_doc_path_prefix, template_nb_path, source_nb_paths).generate()


NbTpltChain('./fitted-','./fitter-template/.ipynb', ['./logr.ipynb', './svr.ipynb']).generate()
```

### Generated Templates

Assuming the template prefix was `./fitted-` like in the example above, the template generator will create the
following notebooks:
- `./fitted-logr.ipynb`
- `./fitted-svr.ipynb`

For example the `./fitted-logr.ipynb` notebok would look like this:
```python
# PyCharm uses `#%%` to delineate cells
# Identify the data to import into the template by assigning an id and type to the cell
# Example `#%% nbtplt my-id code` has an id of 'my-id' and indicates that the cell is a code cell.

#%% nbtplt concrete-model code
from sklearn.linear_model import LogisticRegression
model = LogisticRegression()

#%%
model.fit(X, y)

# Do more things with model
```

## Known Issues


## Author Note
I created this because I couldn't find a Jupyter templating engine. My biggest requirement is that
I wanted to author everything in the notebook itself. Since I use PyCharm, this solution is tailored for the 
PyCharm `#%%` code that creates cells. Extending the code to support native Jupyter notebooks shouldn't be that 
difficult but would probably require editing the cell metadata to identify which cells should be templated.

