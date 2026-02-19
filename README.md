# Exclurad

Fortran code for calculation of radiative corrections to exclusive electroproduction of pions on a nucleon. Current version computes corrections to the unpolarized coincidence cross section and beam asymmetry (aka the fifth structure function). Distinctive features are 
a) Covariant technique of cancellation of the infrared divergence leads to independence of the parameter that splits soft and hard regions of brem photons and 
b) Integration over the brem photon phase space is exact, not relying on the peaking approximation. 
MAID and AO are used to model the reaction mechanism. The code is extendable to any exclusive electron scattering with two-body breakup, such as p(e,e'K)Lambda, d(e,e'p)n, 3He(e,e'p)d, etc.

## References
```
QED RADIATIVE CORRECTIONS IN PROCESSES OF EXCLUSIVE PION ELECTROPRODUCTION.
By A. Afanasev (Jefferson Lab), I. Akushevich (Duke U.), V. Burkert, K. Joo (Jefferson Lab) 
Published in Phys.Rev.D66:074004,2002
e-Print Archive: hep-ph/0208183 
```
## Links
https://arxiv.org/pdf/hep-ph/0208183.pdf

# Getting Started

## Clone the repository
```
git clone https://github.com/JeffersonLab/exclurad.git
```

## Build the executable
```
cd exclurad/exclurad
./scons-safe
```

If your site environment sets `PYTHONHOME`/`PYTHONPATH` (for example via CVMFS views), plain `scons` may fail with `ModuleNotFoundError: No module named encodings`. The `scons-safe` helper in `exclurad/` unsets those variables only for the SCons process.

## Example input file (input.dat):

```
3       !  1: AO 2: maid98  3: maid2007
0       !  0: Full, 1: Factorizable and Leading log  
1.645   !  bmom - lepton momentum
0.0     !  tmom - momentum per nucleon
1       !  lepton - 1 electron, 2 muon
2       !  ivec - detected hadron (1) p, (2) pi+
0.05      !  vcut - cut on inelasticity (0.) if no cut, negative -- v


10 ! no. of points
1.232 1.232 1.232 1.232 1.232 1.232 1.232 1.232 1.232 1.232 ! W values 
0.4   0.4   0.4   0.4   0.4   0.4   0.4   0.4   0.4   0.4 ! Q^2 values
0.    0.    0.    0.    0.    0.    0.    0.    0.    0. ! Cos(Theta)
10.   50.   90.   130.  170.  190.  230.  270.  310.  350. ! phi values

```

## Example usage:
```
./build/exclurad.exe < input.dat

```

The program reads configuration from standard input. You can therefore run any input file via shell redirection, for example `./build/exclurad.exe < phi.dat`.

## Why a run may stop with only `v1/v2` lines
If output stops after lines like:

```
v1= ... Q2 min= ... Q2 max= ...
v2= ... W  min= ... W  max= ...
```

then your kinematics are outside the MAID interpolation grid. For MAID tables in this repository, the printed limits are typically `0 <= Q2 <= 5` and `1.08 <= W <= 2.0`.

For example, `W=2.2` is out of range, so no radiative-correction rows are produced. Use `W <= 2.0` and valid `Q2` values to get output files (`radcor.dat`, `radsigpl.dat`, `radsigmi.dat`, ...).

A ready-to-run scan file is provided as `exclurad/phi_scan.dat`.

## Analyze and plot outputs
A helper script is provided at `exclurad/tools/analyze_radcor.py`.

Example:

```
cd exclurad
./build/exclurad.exe < phi_scan.dat
python3 tools/analyze_radcor.py --dir . --ebeam 10.6 --ivec 1 --out plots
```

This creates quick-look PNG figures including RC factors vs `Q2`, `W`, `phi`, `cos(theta)`, `y`, and approximate `t`.

## External structure-function mode (no MAID)
If you want RCs for reactions outside MAID (e.g. exclusive phi), use `iphy=4`.
In this mode EXCLURAD does **not** read MAID multipole tables. Instead it reads an external table of hadronic structure functions with 8 columns per row:

`Q2  W  cos(theta_cm)  sigma_T  sigma_L  sigma_TT  sigma_LT  sigma_LTp`

Notes:
- Set `ivec=3` (detected proton, phi recoil) or `ivec=4` (detected phi, proton recoil).
- Point the code to your table via:
  `export EXCLURAD_SF_TABLE=/path/to/your_sf_table.tbl`
- A template input file is provided: `exclurad/phi_external.dat`
- A format example is provided: `exclurad/external_sf_phi_example.tbl`

Example:

```
cd exclurad
export EXCLURAD_SF_TABLE=external_sf_phi_example.tbl
./build/exclurad.exe < phi_external.dat
```

### External SF input format details
Each row in `EXCLURAD_SF_TABLE` represents one kinematic node:

`Q2  W  cos(theta_cm)  sigma_T  sigma_L  sigma_TT  sigma_LT  sigma_LTp`

Where:
- `Q2` is in GeV^2
- `W` is in GeV
- `cos(theta_cm)` is the hadron CM polar angle cosine
- `sigma_*` should be in a **consistent** cross-section unit across all terms (typically microbarn/sr in electroproduction conventions)

In the RC kernel, these are combined as:

`sigma0 = sigma_T + eps*sigma_L + eps*sigma_TT*cos(2phi) + sqrt(eps*(eps+1)/2)*sigma_LT*cos(phi)`

(and polarized term uses `sigma_LTp`).

So if your theory provides only `sigma_T` and `sigma_L`, you can still run by setting:
- `sigma_TT = 0`
- `sigma_LT = 0`
- `sigma_LTp = 0`

This gives RCs for a reduced structure-function model (no transverse-transverse / longitudinal-transverse interference terms).

### Converting theory tables with only sigma_T and sigma_L
Use:

```bash
python3 exclurad/tools/prepare_external_sf.py   --infile my_theory_ST_SL.tbl   --outfile external_sf.tbl
```

Input rows for this helper can be either:
- 5 columns: `Q2 W cos(theta_cm) sigma_T sigma_L`
- 8 columns: full EXCLURAD format

For 5-column rows, `sigma_TT`, `sigma_LT`, and `sigma_LTp` are filled with defaults (0.0 unless overridden).

## Using newer MAID tables
By default the code loads bundled table names (`maid98-*.tbl`, `maid07-*.tbl`).
You can override those paths at runtime with environment variables:

- `EXCLURAD_MAID98_PPPI`
- `EXCLURAD_MAID98_PNPI`
- `EXCLURAD_MAID07_PPPI`
- `EXCLURAD_MAID07_PNPI`
- `EXCLURAD_MAID07_NPPI`

Example:

```
export EXCLURAD_MAID07_PPPI=/path/to/new/maid07-PPpi.tbl
./build/exclurad.exe < phi_scan.dat
```

This lets you test newer/reprocessed MAID-style pion tables without editing source.

## About phi-meson electroproduction
There are now two approaches:
- **MAID/AO modes** (`iphy=1,2,3`): these are pion-model based.
- **External SF mode** (`iphy=4`): provides MAID-free RC evaluation from user-supplied structure functions, and is the recommended path for exclusive phi studies.

For phi production, provide a physically validated external table of
`(Q2, W, cos(theta_cm), sigma_T, sigma_L, sigma_TT, sigma_LT, sigma_LTp)`
at your kinematics.

## Keep your local checkout updated
A helper script is included to pull updates safely:

```bash
./scripts/update_from_git.sh
```

A root-level alias is also provided if you prefer:

```bash
./pull_all.sh
```

Useful options:
- `--remote origin` (default: `origin`)
- `--branch main` (default: current branch)
- auto-stash is **enabled by default**
- `--no-stash` to fail instead of stashing when local changes exist

Examples:

```bash
./pull_all.sh
./scripts/update_from_git.sh --remote origin --branch main --switch-branch
./scripts/update_from_git.sh --no-stash
```


The updater now creates a safety backup branch before merge:
- `backup/pre-update-<branch>-<timestamp>`

If the result is not what you expected, you can recover quickly:

```bash
git branch --list 'backup/pre-update-*'
git checkout backup/pre-update-<branch>-<timestamp>
# or inspect and restore via:
git reflog --date=local
```

If you ever see `line 1: !/usr/bin/env: No such file or directory`, the script shebang is missing `#`. The first line must be exactly `#!/usr/bin/env bash`.

## Troubleshooting SCons/Python startup errors
If you see an error similar to:

```
Fatal Python error: init_fs_encoding
ModuleNotFoundError: No module named 'encodings'
```

run SCons via the wrapper script:

```
./scons-safe
```

Equivalent one-liner if you prefer not to use the script:

```
env -u PYTHONHOME -u PYTHONPATH scons-2.9
```


