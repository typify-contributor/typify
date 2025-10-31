import shutil
from pathlib import Path
from typify.utils.utils import Utils
from typify.preprocessing.preloader import Preloader
from typify.preprocessing.core import GlobalContext
from typify.inferencing.inferencer import Inferencer
from typify.utils.caching import GlobalCache
from typify.utils.logging import logger, LogLevel

package_dir = str(Path(__file__).parent.parent)
stubs_dir = str(package_dir + "/typifystubs")

def run_inference(
    project_dir,
    output_dir=None,
    relative_to=None,
    log_level="off",
    clear_cache=False,
    prune_cache=False,
    dont_cache=False,
    clear_output=False,
    heur=False,
    usage=False,
    topn=1,
    config=None
):
    project_dir = Path(project_dir).resolve()
    default_outdir = project_dir / ".typify"
    outdir = Path(output_dir).resolve() if output_dir else default_outdir
    relative_to = Path(relative_to).resolve() if relative_to else project_dir

    if not Utils.is_valid_directory(project_dir):
        print("Invalid project path given.")
        exit(1)

    default_config = {
        "cache_dir": "{auto}",
        "paths": [f"{stubs_dir}/stdlib/"],
        "inference": {
            "builtins": f"{stubs_dir}/stdlib/builtins.pyi",
            "typing": f"{stubs_dir}/stdlib/typing.pyi",
            "types": f"{stubs_dir}/stdlib/types.pyi",
            "collections.abc": f"{stubs_dir}/stdlib/collections/abc.pyi",
            "__future__": f"{stubs_dir}/stdlib/__future__.pyi",
        },
    }

    if config:
        default_config.update({
            "cache_dir": config.get("cache_dir", default_config["cache_dir"]),
            "paths": config.get("paths", default_config["paths"]),
        })
    config = default_config

    cache_path = (
        Path(GlobalCache.get_system_cache()).resolve()
        if config["cache_dir"] == "{auto}"
        else Path(config["cache_dir"]).resolve()
    )

    if clear_output and outdir.exists():
        shutil.rmtree(outdir)

    outdir.mkdir(parents=True, exist_ok=True)

    log_levels = {
        "off": LogLevel.OFF,
        "info": LogLevel.INFO,
        "debug": LogLevel.DEBUG,
        "trace": LogLevel.TRACE,
        "error": LogLevel.ERROR,
        "warning": LogLevel.WARNING,
    }

    logger.set_level(log_levels[log_level])
    if logger.level != LogLevel.OFF:
        log_file = outdir / "typify.log"
        logger.add_output(open(log_file, "w", encoding="utf-8"))

    Preloader.load(
        cache_path=cache_path,
        clear_cache=clear_cache,
        dont_cache=dont_cache,
        config=config,
        project_dir=project_dir,
    )

    if prune_cache:
        GlobalCache.prune()

    logger.info(f"{logger.emoji_map['summary']} Libraries loaded:", 1)
    for libpath in GlobalContext.libs:
        logger.info(f"   {libpath.as_posix()}")

    logger.info(f"{logger.emoji_map['graph']} Dependency Graph:", 1)
    for meta, deps in GlobalContext.dependency_graph.items():
        joined = ", ".join(repr(dep) for dep in deps)
        logger.info(f"   {repr(meta)} ➜ [{joined}]")

    Inferencer.infer(
        outdir=outdir,
        relative_to=relative_to,
        usage_driven=usage,
        heur_driven=heur,
        topn=topn,
    )

    if GlobalCache.staged_contexts:
        GlobalCache.flush_inference_contexts(cache_path)
        logger.debug(f"{logger.emoji_map['ok']} [Cache] Flushed staged contexts to disk.", trail=1)

    logger.close()