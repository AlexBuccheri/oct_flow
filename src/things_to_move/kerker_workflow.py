""" Kerker vs No Kerker Workflow
"""
from pathlib import Path
from typing import List

from oct_workflow import ground_state_calculation
from components import write_extended_xyz

from kerker_settings import (matrix, static_options, specific_options, meta_keys, default_ada_gpu,
                             kerker_options)


def gnuplot_kerker_script(root: str, job_ids: List[str]) -> str:
    """

    :return:
    """
    string = 'module load gnuplot/5.2 \n'
    string += 'set logscale y \n'
    string += "set ylab 'Change in total energy' \n"

    string += f'plot {root}/{job_ids[0]}/static/convergence u 1:3 w l title "{job_ids[0]} {root}" \n'
    for id in job_ids[1:]:
        string += f'replot {root}/{id}/static/convergence u 1:3 w l title "{id} {root}" \n'

    return string


if __name__ == "__main__":

    use_kerker = False
    root = 'jobs/no_kerker'
    oct_root_ada = '/u/abuc/packages/octopus/_build_kerker/installed'

    if use_kerker:
        root = root.replace('no_', '')
        static_options.update(kerker_options)

    jobs = ground_state_calculation(matrix, static_options, specific_options, meta_keys, default_ada_gpu, oct_root_ada)

    # Write jobs to file
    for job in jobs.values():
        subdir = Path(root, job['directory'])
        Path.mkdir(subdir, parents=True, exist_ok=True)

        for file_type, file_name in [('hash', 'metadata.txt'), ('inp', 'inp'), ('submission', 'run.sh')]:
            with open(subdir / file_name, 'w') as fid:
                fid.write(job[file_type])

        # xyz_file = str(subdir / job['directory']) + '.xyz'
        # # NOTE ALEX. This ref format does not appear to get picked up by vesta
        # # Note, the ASE cell does not have the shifted origin
        # write_extended_xyz(xyz_file, job['structure'])

    print(gnuplot_kerker_script(root, list(jobs.keys())))
