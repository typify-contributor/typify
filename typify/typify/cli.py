import click

from typify import (
	run_infer, 
	run_build, 
	stubs_dir
)

@click.group()
@click.version_option("1.0.0", prog_name="Typify")
def cli():
    """Typify: Static Type Inference Tool"""

@cli.command()
@click.argument("project_dir", type=click.Path(exists=True))
@click.option("--output-dir", type=click.Path(), help="Directory for inferred types output.")
@click.option("--relative-to", type=click.Path(), help="Base directory for relative paths.")
@click.option(
    "--log-level",
    default="off",
    show_default=True,
    type=click.Choice(["off", "info", "debug", "trace", "error", "warning"]),
    help="Verbosity of logging output."
)
@click.option("--clear-cache", is_flag=True, help="Clear the cache before running.")
@click.option("--prune-cache", is_flag=True, help="Remove invalid cache entries.")
@click.option("--dont-cache", is_flag=True, help="Disable cache usage during inference.")
@click.option("--clear-output", is_flag=True, help="Clear the output directory before writing results.")
@click.option("--heur", is_flag=True, help="Enable heuristic-based inference.")
@click.option("--usage", is_flag=True, help="Enable usage-driven inference.")
@click.option("--topn", default=1, show_default=True, help="Number of top inference candidates to output.")
@click.option(
    "--cache-dir",
    default="{auto}",
    show_default=True,
    type=click.Path(),
    help="Path to cache directory. Defaults to system cache."
)
@click.option(
    "--paths",
    multiple=True,
    default=(f"{stubs_dir}/stdlib/",),
    show_default=True,
    help="Additional search paths."
)
def infer(**kwargs):
    """
    Run Typify’s static type inference engine on a Python project.
    """
    config = {
        "cache_dir": kwargs.pop("cache_dir"),
        "paths": list(kwargs.pop("paths")),
    }

    run_infer.run_inference(config=config, **kwargs)

@cli.command()
@click.option("--train-files", required=True, type=click.Path(exists=True))
@click.option("--output-dir", default="typify/index", show_default=True)
@click.option("--max-features", default=20000, show_default=True, help="Maximum features for TF-IDF vectorizer.")
@click.option("--ngram", nargs=2, type=int, default=(1, 2), show_default=True, help="n-gram range for TF-IDF.")
@click.option("--min-df", default=1, show_default=True, help="Minimum document frequency for TF-IDF terms.")
def build(train_files, output_dir, max_features, ngram, min_df):
    """Build a context index from annotated Python files."""
    run_build.build_index(
        train_list_file=train_files,
        output_dir=output_dir,
        max_features=max_features,
        ngram_range=tuple(ngram),
        min_df=min_df,
    )

def main():
    cli()

if __name__ == "__main__":
    main()
