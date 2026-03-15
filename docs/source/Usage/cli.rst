Using SimbaML CLI
==================

SimbaML provides a modern CLI for SBML parsing, BioModels integration, and data generation.

Installation
------------

After installing SimbaML, the ``simba-ml`` command will be available:

    $ simba-ml --help

For detailed help on any command, use:

    $ simba-ml <command> --help

SBML Parsing
------------

Parse and analyze SBML model files locally.

Basic Usage
^^^^^^^^^^^

    $ simba-ml sbml parse <path-to-sbml-file>

This command will:
- Detect SBML Level and Version
- Parse the model structure (species, reactions, parameters, compartments)
- Analyze species types (dynamic vs boundary conditions)
- Display ODE readiness assessment
- Show sample species and reactions
- Display model description

The parser validates:
- SBML file format and compliance
- Presence of kinetic laws for ODE simulation
- Model connectivity and network structure

Options
^^^^^^^

- ``--verbose, -v``: Show detailed parsing information
- ``--species-limit, -s INTEGER``: Number of species to display (default: 5)
- ``--reactions-limit, -r INTEGER``: Number of reactions to display (default: 5)
- ``--export {csv}``: Export model data to CSV format (currently supported)
- ``--output-dir, -o PATH``: Output directory for exports (default: ./sbml_exports)
- ``--quiet, -q``: Suppress visual output (JSON output only)

Examples
^^^^^^^^

Parse a local SBML file:

    $ simba-ml sbml parse Garde2020.xml

Parse with verbose output and custom display limits:

    $ simba-ml sbml parse model.xml --verbose --species-limit 10 --reactions-limit 10

Export model data to CSV format:

    $ simba-ml sbml parse model.xml --export csv --output-dir ./exported_data

Get JSON output (quiet mode, useful for scripts):

    $ simba-ml sbml parse model.xml --quiet

BioModels Integration
---------------------

Search and download SBML models from the `BioModels Database <https://www.ebi.ac.uk/biomodels/>`_.

Search for Models
^^^^^^^^^^^^^^^^^

    $ simba-ml biomodels search <query> [--limit <number>]

The search command queries the BioModels REST API and displays:
- Model ID (e.g., BIOMD0000000505)
- Model name
- Format (SBML)

Search examples:

    # Search for SIR models (limit 3 results)
    $ simba-ml biomodels search "SIR" --limit 3

    # Search for oscillation models (default 10 results)
    $ simba-ml biomodels search "oscillation"

    # Search for cancer models
    $ simba-ml biomodels search "cancer"

Download Models
^^^^^^^^^^^^^^^

    $ simba-ml biomodels download <model-id> [--output-dir <path>]

Downloads a specific BioModels model and saves it as an SBML XML file.

Options:

- ``--output-dir, -o PATH``: Directory to save the model (default: ./biomodels_downloads)

Download examples:

    # Download a specific model
    $ simba-ml biomodels download BIOMD0000000505

    # Download to a custom directory
    $ simba-ml biomodels download BIOMD0000000505 --output-dir ./my_models

Complete Workflow
-----------------

Here's a typical workflow for finding and analyzing a model:

1. **Search for models of interest:**

    $ simba-ml biomodels search "SIR"

2. **Download a model:**

    $ simba-ml biomodels download BIOMD0000000982

3. **Parse and analyze the downloaded model:**

    $ simba-ml sbml parse BIOMD0000000982_url.xml

4. **Export data for machine learning:**

    $ simba-ml sbml parse BIOMD0000000982_url.xml --export csv --output-dir ./sir_data

5. **Get JSON output for programmatic use:**

    $ simba-ml sbml parse BIOMD0000000982_url.xml --quiet

Legacy CLI
----------

For backward compatibility, the legacy CLI interface is still available:

    $ python -m simba_ml.cli <command>

The modern CLI (``simba-ml``) is recommended for new workflows as it provides better formatting and improved user experience.
