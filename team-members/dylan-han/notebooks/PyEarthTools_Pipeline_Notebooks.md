# PyEarthTools Pipeline Notes

## 1. Basic

`pyearthtools.pipeline` is designed to build a modular sequence of operations for data preparation.  
Compared with simple transforms in `pyearthtools.data`, pipelines are more structured, composable, and reversible, which makes them much more suitable for machine learning workflows and other downstream tasks.

The core object is the `Pipeline` class. A pipeline usually begins with a `pyearthtools.data.Index`, which acts as the data source, and then applies a sequence of operations step by step.

### Key ideas
- A pipeline is a controlled flow of data processing.
- The first step is usually a data index.
- Later steps modify, convert, or prepare the data.
- Pipelines can be indexed like normal data sources.
- Operations are applied in order.
- Pipelines support `undo`, which allows transformed data to be restored to its original form.

### Example concept
A simple pipeline may:
1. Read ERA5 data from an index
2. Convert the result from `xarray` to `numpy`

This means the pipeline not only retrieves data, but also prepares it directly in the required format.

### Why it matters
The notebook stresses that pipelines should be built gradually.  
A good practice is to start with a small pipeline, inspect the result, and then add more steps only after confirming that the current output is correct.

---

## 2. Branching

Branching extends the normal linear pipeline model.  
Instead of processing data through a single straight sequence, a pipeline can split into multiple branches and process data in different ways at the same time.

Branches are created by passing tuples as pipeline steps.

### Main branching patterns

#### Multiple inputs
A pipeline can start from multiple data sources at once.  
This is useful when combining data from:
- different datasets
- different versions of the same dataset
- differently prepared inputs

#### Pipelines within branches
Each branch can contain its own mini-pipeline.  
This allows one branch to apply extra processing while another branch remains unchanged.

#### Merge
After branching, outputs can be merged back together.  
Special merge operations are available for combining tuple outputs into a single result.

#### Within-pipeline branching
Branching does not need to happen only at the beginning.  
A pipeline can take one input, copy it, and send copies through different processing paths.  
The results are then returned as a tuple, preserving the order of the branches.

#### Mapped branches
Instead of copying the same sample into each branch, tuple elements can be mapped directly across branches.  
This is useful when different inputs should be processed by different operations.

#### Empty branches
If one branch should leave the data unchanged, `pyearthtools.pipeline.Empty()` can be used as a placeholder.

### Why branching is useful
Branching is helpful when:
- comparing multiple preparation methods
- combining several data sources
- applying parallel transformations
- building more flexible and reusable workflows

---

## 3. Modification

`pyearthtools.pipeline.modifications` changes how a pipeline retrieves or manages data.  
Unlike normal operations, which transform the data after retrieval, modifications affect the retrieval process itself.

### Cache
Caching is one of the main modification features.

A cache works by:
1. checking whether processed data already exists
2. loading it if available
3. otherwise generating it and saving it for future use

This makes repeated access much faster.

Important detail:
- Looking up cached data may itself trigger creation
- Therefore, checking raw existence should be done through the underlying pattern rather than normal retrieval

### Index modifiers
Index modifiers change the requested index before retrieval.  
This means the user’s request can be altered dynamically.

Possible index modifications include:
- replacing the index
- adding offsets
- adjusting the retrieval behaviour

This is useful when the actual sample needed is related to, but not identical to, the requested index.

### Temporal retrieval
A related idea is temporal retrieval, where time-based indices can be shifted or adjusted.  
This is especially useful for time-series workflows, such as:
- fetching earlier or later timesteps
- building lagged inputs
- creating temporal context windows

### Why modifications matter
Modifications make pipelines smarter.  
They help control not just *how data is processed*, but also *how data is fetched in the first place*.

---

## 4. Operation

Operations are the individual processing steps inside a pipeline.  
They define how data is transformed after being retrieved from the source index.

`pyearthtools.pipeline.operations` contains the built-in operation library.

### Framework-specific operations
Different frameworks have their own operation sets, such as:
- `xarray`
- `numpy`
- `dask`

This is important because the correct operation type should match the current data format.

For example:
- if the data is an `xarray` object, use `xarray` operations
- if the data has been converted to `dask`, then use `dask` operations

### Typical workflow
A pipeline can be extended step by step:
1. retrieve data from an index
2. rename variables
3. fill missing values
4. convert data type or framework
5. apply more framework-specific transformations

### Examples of operations shown
- renaming metadata
- filling NaN values
- converting between `xarray`, `numpy`, and `dask`
- reshaping or rearranging data
- changing orientation or coordinate conventions

### Important design idea
Operations should be added incrementally and checked frequently.  
This makes it easier to understand the pipeline and debug problems early.

### Reversibility
Another important property is that many operations can be undone.  
This allows a processed sample to be transformed back to its earlier form, which is useful for:
- interpretability
- debugging
- end-to-end workflows where outputs need to be mapped back to original coordinates or structure

---

## 5. Patterns

The Patterns notebook introduces additional syntax and design patterns that make pipelines easier to build, organise, and reuse.

### Named pipelines
Long pipelines can be split into smaller sub-pipelines, each with its own name.  
These named pipelines can later be accessed through the `.named` attribute.

Benefits:
- better readability
- easier debugging
- improved reuse of important pipeline stages
- easier inspection of intermediate processing blocks

### Pipe operator (`|`)
Pipelines can be combined using the `|` operator.  
This provides a convenient way to join multiple pipeline segments together without manually rewriting them into one large constructor.

This makes pipeline composition cleaner and more expressive.

### Reversed pipeline
A pipeline can be reversed using the `.reversed` attribute.  
This creates a pipeline that applies the inverse of previous transformations.

This is especially useful when:
- preprocessing data before a model
- then converting model outputs back into the original structure or coordinate system

### End-to-end inference pattern
One of the most useful patterns is combining:
1. a preprocessing pipeline
2. a model inference step
3. the reversed preprocessing pipeline

This creates a full end-to-end workflow where:
- raw data is prepared for the model
- the model produces predictions
- predictions are converted back into a meaningful Earth-system data format

### Why these patterns are valuable
These patterns improve:
- modularity
- readability
- reusability
- maintainability

They also make it easier to build large workflows without losing access to the important internal stages.

---

# Overall Summary

`pyearthtools.pipeline` provides a flexible framework for building structured, reversible, and reusable data workflows.

Its main strengths are:
- modular step-by-step design
- support for branching
- retrieval-time modifications such as caching
- framework-aware operations
- advanced syntax patterns for combining and reversing pipelines

In practice, it is best used by building pipelines gradually, checking outputs often, and organising complex workflows into smaller, named components.
