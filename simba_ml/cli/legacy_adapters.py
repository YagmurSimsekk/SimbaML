"""Legacy command adapters for backward compatibility."""

import click
from simba_ml.cli.commands.sbml import parse as sbml_parse
from simba_ml.cli.commands.biomodels import search as biomodels_search, download as biomodels_download
from simba_ml.cli.commands.steady_state import generate as steady_state_generate


@click.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("--verbose", "-v", is_flag=True, help="Show detailed parsing information")
@click.option("--species-limit", "-s", default=5, help="Number of species to display (default: 5)")
@click.option("--reactions-limit", "-r", default=5, help="Number of reactions to display (default: 5)")
@click.option("--export", "-e", type=click.Choice(['csv', 'json', 'npz']), help="Export data in specified format")
@click.option("--output-dir", "-o", default="./sbml_ml_data", help="Output directory for exported data")
@click.option("--quiet", "-q", is_flag=True, help="Suppress visual output, only export data")
def parse_sbml(file, verbose, species_limit, reactions_limit, export, output_dir, quiet):
    """Parse an SBML file and print a summary of the model (Legacy)."""
    # Convert to Path object for compatibility
    from pathlib import Path
    file_path = Path(file)
    
    # Call the new implementation with all options
    ctx = click.get_current_context()
    ctx.invoke(sbml_parse, file=file_path, verbose=verbose, 
               species_limit=species_limit, reactions_limit=reactions_limit, 
               export=export, output_dir=Path(output_dir), quiet=quiet)


@click.group()
def biomodels():
    """BioModels Database commands (Legacy)."""
    pass


# Add the new subcommands to the legacy biomodels group
biomodels.add_command(biomodels_search, name="search")
biomodels.add_command(biomodels_download, name="download")


@click.group() 
def steady_state():
    """Generate steady-state data from SBML models (Legacy)."""
    pass


# Add the new subcommands to the legacy steady-state group  
steady_state.add_command(steady_state_generate, name="generate")
