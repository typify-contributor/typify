import subprocess
import tempfile
import json

from pathlib import Path

from typify import stubs_dir
from typify.utils.utils import Utils
from typify.preprocessing.preloader import Preloader
from typify.preprocessing.core import GlobalContext
from typify.inferencing.inferencer import Inferencer
from typify.utils.caching import GlobalCache
from typify.utils.logging import logger, LogLevel

def find_python_projects(root: Path) -> list[str]:
	projects: list[str] = []

	def is_candidate(directory: Path, is_root: bool = False) -> bool:
		try:
			if is_root and (directory / '__init__.py').is_file():
				return True
			if (directory / '__init__.py').is_file():
				return False
			if any(f.is_file() and f.suffix == '.py' and f.name != '__init__.py' for f in directory.iterdir()):
				return True
			for sub in directory.iterdir():
				if sub.is_dir() and (sub / '__init__.py').is_file():
					return True
			return False
		except Exception:
			return False

	def recurse(directory: Path, is_root: bool = False):
		try:
			if is_candidate(directory, is_root):
				projects.append(directory.resolve().as_posix())
			for sub in directory.iterdir():
				if sub.is_dir():
					recurse(sub)
		except Exception:
			pass

	recurse(root, is_root=True)

	seen, uniq = set(), []
	for p in projects:
		if p not in seen:
			uniq.append(p)
			seen.add(p)

	return uniq

def run_project(
	project_dir,
	output_log,
	log_level="off",
	clear_cache=False,
	prune_cache=False,
	cache=False,
	heur=False,
	usage=False,
	topn=1,
	config=None,
):
	project_dir = Path(project_dir).resolve()

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
		logger.add_output(open(output_log, "w", encoding="utf-8"))

	Preloader.load(
		cache_path=cache_path,
		clear_cache=clear_cache,
		cache=cache,
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

	total_counts, project_lib, corrected_sequences, inferred_types =  Inferencer.preinfer(
		usage_driven=usage,
		heur_driven=heur,
		topn=topn
	)

	inferred_types = Inferencer.infer(
		total_counts=total_counts,
		project_lib=project_lib,
		corrected_sequences=corrected_sequences,
		topn=topn,
	)

	if GlobalCache.staged_contexts:
		GlobalCache.flush_inference_contexts(cache_path)
		logger.debug(f"{logger.emoji_map['ok']} [Cache] Flushed staged contexts to disk.", trail=1)

	logger.close()
	return inferred_types

def inferp(
    project_dir,
    output_types=None,
    output_log=None,
    log_level="off",
    clear_cache=False,
    prune_cache=False,
    cache=False,
    heur=False,
    usage=False,
    topn=1,
    cache_dir="{auto}",
    paths=(f"{stubs_dir}/stdlib/",),
):
    config = {
        "cache_dir": cache_dir,
        "paths": list(paths),
    }

    project_dir = Path(project_dir).resolve()

    if output_types is None or output_log is None:
        outdir = project_dir / ".typify"
        outdir.mkdir(parents=True, exist_ok=True)
    else:
        outdir = None

    output_types = (
        (outdir / "types.json") if output_types is None else Path(output_types).resolve()
    )
    output_log = (
        (outdir / "typify.log") if output_log is None else Path(output_log).resolve()
    )

    inferred_project = run_project(
        project_dir=project_dir,
        output_log=output_log,
        log_level=log_level,
        clear_cache=clear_cache,
        prune_cache=prune_cache,
        cache=cache,
        heur=heur,
        usage=usage,
        topn=topn,
        config=config,
    )

    with open(output_types, "w", encoding="utf-8") as f:
        json.dump(inferred_project, f, indent="\t")

def infer(
    repo_dir,
    output_types=None,
    output_log=None,
    log_level="off",
    clear_cache=False,
    prune_cache=False,
    cache=False,
    heur=False,
    usage=False,
    topn=1,
    cache_dir="{auto}",
    paths=(f"{stubs_dir}/stdlib/",),
):
    repo_dir = Path(repo_dir).resolve()

    if not Utils.is_valid_directory(repo_dir):
        print("Invalid repository path given.")
        exit(1)

    projects = find_python_projects(repo_dir)
    all_inferred: dict = {}

    outdir = repo_dir / ".typify"
    outdir.mkdir(parents=True, exist_ok=True)
    output_types = outdir / "types.json" if output_types is None else Path(output_types).resolve()
    output_log = outdir / "typify.log" if output_log is None else Path(output_log).resolve()

    for project in projects:
        print(f"Running inference on project: {project}")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_types = Path(temp_dir) / "types.json"
            temp_log = Path(temp_dir) / "typify.log"

            cmd = [
                "typify", "inferp", project,
                "--output-types", str(temp_types),
                "--output-log", str(temp_log),
                "--log-level", log_level,
                "--topn", str(topn),
                "--cache-dir", cache_dir,
            ]

            for p in paths:
                cmd.extend(["--paths", p])

            if clear_cache:
                cmd.append("--clear-cache")
            if prune_cache:
                cmd.append("--prune-cache")
            if cache:
                cmd.append("--cache")
            if heur:
                cmd.append("--heur")
            if usage:
                cmd.append("--usage")

            subprocess.run(cmd, check=True)

            with open(temp_types, "r", encoding="utf-8") as f:
                project_types = json.load(f)
                all_inferred.update(project_types)

            with open(temp_log, "r", encoding="utf-8") as f:
                log_contents = f.read()
            with open(output_log, "a", encoding="utf-8") as out_log:
                out_log.write(f"Log for project: {project}\n")
                out_log.write(log_contents)
                out_log.write("\n\n")

    with open(output_types, "w", encoding="utf-8") as f:
        json.dump(all_inferred, f, indent="\t")

