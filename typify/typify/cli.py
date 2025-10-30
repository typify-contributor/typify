import click

from typify import run_infer
from typify import run_build

@click.group()
@click.version_option("1.0.0", prog_name="Typify")
def cli():
    """Typify: Static Type Inference Tool"""

@cli.command()
@click.argument("project_dir", type=click.Path(exists=True))
@click.option("--output-dir", type=click.Path(), help="Output directory for inferred types.")
@click.option("--relative-to", type=click.Path(), help="Base directory for relative paths.")
@click.option("--log-level", default="off", type=click.Choice(["off","info","debug","trace","error","warning"]))
@click.option("--clear-cache", is_flag=True)
@click.option("--prune-cache", is_flag=True)
@click.option("--dont-cache", is_flag=True)
@click.option("--clear-output", is_flag=True)
@click.option("--topn", default=1, type=int)
@click.option("--heur", is_flag=True)
@click.option("--usage", is_flag=True)
def infer(**kwargs):
    """Run usage-driven type inference on a Python project."""
    run_infer.run_inference(**kwargs)

@cli.command()
@click.option("--train-files", required=True, type=click.Path(exists=True))
@click.option("--output-dir", default="typify/index", show_default=True)
@click.option("--max-features", default=20000, show_default=True, help="Max features for TF-IDF.")
@click.option("--ngram", nargs=2, type=int, default=(1, 2), show_default=True, help="n-gram range for TF-IDF.")
@click.option("--min-df", default=1, show_default=True, help="Minimum document frequency for terms.")
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
