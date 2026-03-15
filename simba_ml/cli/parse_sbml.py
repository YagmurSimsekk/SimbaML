import click
import json
import os
from simba_ml.sbml_parser.main_parser import MainSBMLParser, UnsupportedSBMLVersionError, SBMLParsingError
from simba_ml.sbml_parser.ml_exporter import SBMLExporter

@click.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("--verbose", "-v", is_flag=True, help="Show detailed parsing information")
@click.option("--species-limit", "-s", default=5, help="Number of species to display (default: 5)")
@click.option("--reactions-limit", "-r", default=5, help="Number of reactions to display (default: 5)")
@click.option("--export", "-e", type=click.Choice(['csv', 'json', 'npz']), help="Export ML-ready data in specified format")
@click.option("--output-dir", "-o", default="./sbml_ml_data", help="Output directory for exported data (default: ./sbml_ml_data)")
@click.option("--quiet", "-q", is_flag=True, help="Suppress visual output, only export data")
def parse_sbml(file, verbose, species_limit, reactions_limit, export, output_dir, quiet):
    """Parse an SBML file and print a summary of the model."""
    try:
        sbml_parser = MainSBMLParser(file)
        result = sbml_parser.process()
        
        # If quiet mode and no export, just export the JSON to stdout and return
        if quiet and not export:
            exporter = SBMLExporter(result)
            ml_dataset = exporter.get_ml_dataset()
            click.echo(json.dumps(ml_dataset, indent=2, default=str))
            return
        
        # Print header (unless quiet mode)
        if not quiet:
            click.echo(click.style("=" * 60, fg='green'))
            click.echo(click.style(f"SBML Model Parsing Results", fg='green', bold=True))
            click.echo(click.style("=" * 60, fg='green'))
            click.echo()
        
        # Basic info
        info = result['sbml_info']
        
        if not quiet:
            click.echo(click.style(f"📄 File:", fg='blue', bold=True) + f" {file}")
            click.echo(click.style(f"📋 Model:", fg='blue', bold=True) + f" {info['model_name']} (ID: {info['model_id']})")
            click.echo(click.style(f"🔢 SBML Level:", fg='blue', bold=True) + f" {info['level']}, Version: {info['version']}")
            click.echo()
        
        # Statistics
        if not quiet:
            click.echo(click.style("📊 Model Statistics:", fg='cyan', bold=True))
        else:
            click.echo(f"📊 Model Statistics:")
        click.echo(f"  • Species: {info['num_species']}")
        click.echo(f"  • Reactions: {info['num_reactions']}")
        click.echo(f"  • Parameters: {info['num_parameters']}")
        click.echo(f"  • Compartments: {info['num_compartments']}")
        
        if 'num_events' in info:
            click.echo(f"  • Events: {info['num_events']}")
        if 'num_constraints' in info:
            click.echo(f"  • Constraints: {info['num_constraints']}")
        click.echo()
        
        # ODE suitability check
        has_kinetic_laws = any(r.get('kinetic_law') is not None for r in result['reactions'])
        if result['reactions'] and not has_kinetic_laws:
            click.echo(click.style("⚠️  Warning:", fg='yellow', bold=True) + " No kinetic laws found - this model may not be suitable for ODE simulation")
        elif result['reactions'] and has_kinetic_laws:
            click.echo(click.style("✅ ODE Ready:", fg='green', bold=True) + " Model contains kinetic laws suitable for ODE simulation")
        click.echo()
        
        # Sample species
        if result['species']:
            click.echo(click.style(f"🧬 Sample Species (showing {min(species_limit, len(result['species']))}):", fg='magenta', bold=True))
            for i, species in enumerate(result['species'][:species_limit]):
                boundary = " (boundary)" if species.get('boundary_condition') else ""
                initial = ""
                if species.get('initial_concentration') is not None:
                    initial = f" [C₀={species['initial_concentration']}]"
                elif species.get('initial_amount') is not None:
                    initial = f" [A₀={species['initial_amount']}]"
                click.echo(f"  {i+1}. {species['id']} in {species['compartment']}{boundary}{initial}")
            if len(result['species']) > species_limit:
                click.echo(f"  ... and {len(result['species']) - species_limit} more")
            click.echo()
        
        # Sample reactions
        if result['reactions']:
            click.echo(click.style(f"⚗️  Sample Reactions (showing {min(reactions_limit, len(result['reactions']))}):", fg='red', bold=True))
            for i, reaction in enumerate(result['reactions'][:reactions_limit]):
                reactants = " + ".join([f"{r['species']}" for r in reaction.get('reactants', [])])
                products = " + ".join([f"{p['species']}" for p in reaction.get('products', [])])
                reversible = " ⇌ " if reaction.get('reversible', False) else " → "
                kinetic_info = " ✓" if reaction.get('kinetic_law') else " ✗"
                click.echo(f"  {i+1}. {reaction['id']}: {reactants}{reversible}{products}{kinetic_info}")
            if len(result['reactions']) > reactions_limit:
                click.echo(f"  ... and {len(result['reactions']) - reactions_limit} more")
            click.echo()
        
        # Compartments
        if result['compartments']:
            click.echo(click.style("🏠 Compartments:", fg='cyan', bold=True))
            for comp in result['compartments']:
                size_info = f" (size: {comp['size']})" if comp.get('size') is not None else ""
                click.echo(f"  • {comp['id']}{size_info}")
            click.echo()
        
        # Verbose output
        if verbose:
            click.echo(click.style("🔍 Detailed Information:", fg='white', bold=True))
            if info.get('notes'):
                click.echo("Notes:")
                click.echo(f"  {info['notes'][:200]}{'...' if len(info['notes']) > 200 else ''}")
                click.echo()
            
            # Unit information (Level 3)
            if info.get('substance_units'):
                click.echo(f"Substance Units: {info['substance_units']}")
            if info.get('time_units'):
                click.echo(f"Time Units: {info['time_units']}")
            if info.get('volume_units'):
                click.echo(f"Volume Units: {info['volume_units']}")
        
        # ML Data Export
        if export:
            if not quiet:
                click.echo()
                click.echo(click.style("🔬 Exporting data...", fg='cyan', bold=True))
            
            try:
                exporter = SBMLExporter(result)
                exported_files = exporter.export_to_files(output_dir, format=export)
                
                if not quiet:
                    click.echo(click.style(f"📁 Data exported to: {output_dir}", fg='green'))
                    for data_type, file_path in exported_files.items():
                        click.echo(f"  • {data_type}: {os.path.basename(file_path)}")
                    
                    # Show some ML statistics
                    ml_dataset = exporter.get_ml_dataset()
                    click.echo()
                    click.echo(click.style("📊 ML Dataset Summary:", fg='cyan', bold=True))
                    if 'matrices' in ml_dataset:
                        S = ml_dataset['matrices']['stoichiometry']
                        A = ml_dataset['matrices']['adjacency']
                        click.echo(f"  • Stoichiometry matrix: {S.shape}")
                        click.echo(f"  • Adjacency matrix: {A.shape}")
                        click.echo(f"  • Network density: {(A.sum() / (A.shape[0] * A.shape[1]) * 100):.1f}%")
                    
                    if 'features' in ml_dataset:
                        features = ml_dataset['features']
                        for feat_name, feat_array in features.items():
                            click.echo(f"  • {feat_name} features: {feat_array.shape}")
                else:
                    # Quiet mode - just print file paths
                    for file_path in exported_files.values():
                        click.echo(file_path)
                        
            except Exception as e:
                click.echo(click.style(f"❌ Export Error: {e}", fg='red'), err=True)
                raise click.Abort()
        
        if not quiet:
            click.echo(click.style("✨ Parsing completed successfully!", fg='green', bold=True))
        
    except UnsupportedSBMLVersionError as e:
        click.echo(click.style(f"❌ Unsupported SBML Version: {e}", fg='red'), err=True)
        raise click.Abort()
    except SBMLParsingError as e:
        click.echo(click.style(f"❌ SBML Parsing Error: {e}", fg='red'), err=True)
        raise click.Abort()
    except Exception as e:
        click.echo(click.style(f"❌ Unexpected Error: {e}", fg='red'), err=True)
        raise click.Abort()
