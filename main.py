# import statements
from e2edna import *


'''
E2EDNA "End-to-end DNA" Protocol for folding and structure evaluation of ssDNA aptamers 
and analysis of their binding to analyte molecules.

Implemented in the Tinker molecular dynamics engine for use with the AMOEBA polarizable force field,
with auxiliary tools: seqfold, MacroMoleculeBuilder and MDAnalysis.

Michael Kilgour*, Tao Liu and Lena Simine, 2021
*mjakilgour aat gmail doot com


Copyright (C) 2021 Michael Kilgour and E2EDNA contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''


### Set parameters
params = {}

# Device and working directory
params['device'] = 'cluster' # 'local' or 'cluster' for testing and deployment, respectively
params['explicit run enumeration'] = False # if True, the next run is fresh, in directory 'run%d'%run_num. If False, regular behaviour, including pick-up on a preivous run. Note: ONLY USE True FOR FRESH RUNS
if params['device'] == 'cluster':
    params['run num'] = get_input() # get run_num from command line, default = 0 (fresh run)
elif params['device'] == 'local':
    params['run num'] = 0 # manual setting, for 0, do a fresh run, for != 0, pickup on a previous run.

# Simulation parameters for Tinker software
params['simulation type'] = 'free' # 'free', 'binding' or 'analysis' - branch into different routes in the __main__ function below.
# note that for 'binding' we require a pre-positioned 'repStructure.xyz' of aptamer and optionally binding coordinates.
params['reaction coordinates'] = [[26,213],[53,185]] # key pairs of atom indices whose distances we will monitor and analyze. An example is given here.
params['force field'] = 'AMOEBA' # AMOEBA is only working force-field. Can be updated to run with other Tinker force-fields.
params['target'] = 'UTP-4' # analyte molecule - note parameters will not transfer between force-fields
params['minimization gradrms'] = 0.05 # flag that minimization is converged. 0.1-0.01 is ok usually
params['equilibration time'] = 1 # equilibration time in nanoseconds
params['sampling time'] = 10 # sampling time in nanoseconds
params['time step'] = 2.0 # in femtoseconds
params['num charges'] = 4 # number of positive charges (Na+) to add to simulation box to counter the analyte (UTP is negatively charged). For a positive analyte, must change the neutralization protocol to add anions.
params['NaCl concentration'] = 163 # concentration of NaCl in MD simulation box in mmol - note that seqfold does not allow for modulation of ionic strength in secondary structure prediction, but NUPACK does.
params['box offset'] = 5 # in angstroms. Box size will be order of longest molecule dimension + 2 * vdW radius + 2 * box offset
params['print step'] = 1.0 # printout step in picoseconds
params['heavy hydrogen'] = False # True or False - yes means hydrogens have extra mass (hydrogen mass repartitioning), allowing, in theory, longer time-steps up to 3-4 fs
params['outside secondary structure'] = False # if True, skip seqfold or NUPACK, use a secondary structure manually coded as a list in a relevant .npy file

# analyte placement - only relevant if 'simulation type' is 'binding'
params['analyte position'] = 'random' # 'random' - will be at least 2 nm from the aptamer in one of 8 cubic directions, 'manual' places the aptamer center at the given coordinates relative to origin
if params['analyte position'] == 'manual':
    params['analyte coordinates'] = [10, 10, 10] # places analyte [X, Y, Z] angstroms from the origin

# AMOEBA parameters
params['vdW radius'] = 12  # van der Waals radius
params['polarization version'] = 'OPT4' # OPT3 or OPT4 - 4 is slower but more accurate
params['polar eps'] = 1e-5  # induced dipole convergence parameter. Default = 1e-6
params['polar predict'] = True  # whether to run with polar-predict or not

# User-specific paths
if params['device'] == 'local': # choose to run on a local device, hence, specify paths on the local device
    # paths to Tinker utilities
    params['minimize path'] = 'minimize'
    params['dynamic path'] = 'dynamic'
    params['pdbxyz path'] = 'pdbxyz'
    params['xyzedit path'] = 'xyzedit'
    params['archive path'] = 'archive'
    # directory which holds all the runs
    params['workdir'] = 'C:/Users\mikem\Desktop/tinkerruns'
    # MacroMolecule builder executable and utilities
    params['mmb'] = 'C:/Users/mikem/Desktop/Installer.2_14.Windows/MMB.2_14.exe'

elif params['device'] == 'cluster':
    # Below are our examples. All need to be set to the Tinker executables on your system.
    params['minimize path'] = 'sh ~/projects/def-simine/programs/tinker9/bin/cc70/gpu-m/minimize9.sh'
    params['dynamic path'] = 'sh ~/projects/def-simine/programs/tinker9/bin/cc70/gpu-m/dynamic9.sh'
    params['pdbxyz path'] = '~/projects/def-simine/programs/tinker8/pdbxyz'
    params['xyzedit path'] = '~/projects/def-simine/programs/tinker8/xyzedit'
    params['archive path'] = '~/projects/def-simine/programs/tinker8/archive'
    params['workdir'] = '/home/kilgourm/scratch/simruns' # specify your working directory here
    params['mmb'] = '~/projects/def-simine/programs/MMB/Installer.2_14.Linux64/MMB.2_14.Linux64'

# Copy over MMB files
params['mmb params'] = 'lib/MMB/parameters.csv'
params['mmb template'] = 'lib/MMB/commands.template.dat'

# Find analyte-specific files
if params['force field'] == 'AMOEBA':
    # waters - force-field dependent
    params['waterbox'] = 'lib/water/waterbox.in'
    params['water'] = 'lib/water/water.xyz'

    # tinker utilities - force-field dependent
    # these input files are required for some operations during a simulation.
    params['grablastframe'] = 'lib/infiles/grablastframe.in'
    params['movesomething'] = 'lib/infiles/movesomething.in'
    params['killWater'] = 'lib/infiles/killWater3.in'
    params['addIons'] = 'lib/infiles/addIons.in'
    params['addSodium'] = 'lib/infiles/addSodium.in'
    params['addChloride'] = 'lib/infiles/addChloride.in'
    params['origin'] = 'lib/infiles/origin.in'

    if params['target'] == 'UTP-4':
        params['analyte xyz'] = 'lib/UTP-4/UTP-4.xyz'

        # copy Tinker keyfiles - anaylte-specific due to custom force-field parameters
        params['min key'] = 'lib/keyfiles/UTP-4/minimize.key'
        params['equil key'] = 'lib/keyfiles/UTP-4/equilibrate.key'
        params['dyn key'] = 'lib/keyfiles/UTP-4/dynamics.key'
        params['combined params key'] = 'lib/keyfiles/UTP-4/params_combined.key'


'''
==============================================================
==============================================================
==============================================================
'''

if __name__ == '__main__':  # main function to run e2edna pipeline
    sequence = 'GCTTTGC'  # minimal hairpin as an example
    e2edna = e2edna(sequence, params)  # create an e2edna object called "e2edna"
    if params['simulation type'] == 'free':
        reactionCoordinates = e2edna.runFreeAptamer() # retrieve reaction coordinates from free aptamer trajectory
    elif params['simulation type'] == 'binding':
        reactionCoordinates = e2edna.runBinding() # retrieve reaction coordinates from binding complex trajectory
    elif params['simulation type'] == 'analysis': # just run trajectory analysis if we've already run sampling
        reactionCoordinates = e2edna.trajectoryAnalysis('complex','coarse_complex_sampled.arc.xyz', params['reaction coordinates'], 0, 2)
    saveOutputs(params, reactionCoordinates)
