# Replication Package for Typify

Typify is a **usage-driven static type inference engine** for Python that automatically predicts precise type annotations for variables, parameters, and return values - even in unannotated codebases.  
It performs multi-pass analysis with **call-site driven inference**, **recursive fixpoint resolution**, and **accumulative type unification**, producing high-fidelity inferred annotations.

---

## Features
- Usage-driven inference (based on actual call-site behavior)
- Recursive and interprocedural analysis with fixpoint iteration
- Support for `TypeVar`, `TypeVarTuple`, `Union`, and generic structures
- Incremental rebuilds and global caching for large projects
- Benchmarking tools for comparison with existing inference engines

---

## Installation

You can install Typify in a fresh environment to avoid dependency conflicts.

```bash
# Create a fresh environment
conda create -n typify-env python=3.9 -y
conda activate typify-env

# Clone the repository
git clone https://github.com/typify-contributor/typify.git
cd typify

# Install
pip install -e typify 
```
---

## Example: Running Typify on a Sample Project

In the `typify` directory, there is a sample project named `sample_project`:

We can run Typify on it as follows:

```bash
typify infer sample_project
```

After completion, Typify will output inferred types in JSON format under the `sample_project/.typify/` directory. Use `typify infer --help` for more options.

---

## Development Notes

- Requires **Python 3.9+** environment
- It will work on any OS, but it is explicitly tested on **Ubuntu 22.04 / Debian 12 / WSL2 / Windows 11**
- Compatible with both local and large-scale dataset runs

---

## Citation

Coming soon.

---

## License

Typify is released under the MIT License. See [LICENSE](LICENSE) for details.