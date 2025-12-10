import argparse
import sst
import sys #TODO remove

from sst import UnitAlgebra
from sst.merlin.base import *
from sst.merlin.topology import *
from sst.merlin.endpoint import *
from sst.merlin.interface import *
from sst.ember import *

def main(args):

    ###############################################################
    #### Pull out the command line arguments
    ###############################################################

    # Name of the application communication pattern to model
    app_name = args.app

    # Number of jobs to model.  Each job will be the same size
    num_jobs = args.jobs

    # Number of iterations of the communication pattern to run per job
    iterations = args.iters

    ###############################################################
    ## Get the network parameters
    ###############################################################

    # UnitAlgebra constants used for computing network parameters
    ua_two = UnitAlgebra("2")
    ua_one_pt_five = UnitAlgebra("1.5")
    ua_two = UnitAlgebra("2")
    ua_three = UnitAlgebra("3")

    # Link bandwidth
    link_bw = UnitAlgebra("4GB/s")
    # Make xbar_bw 1.5x link_bw
    xbar_bw = link_bw * ua_one_pt_five

    # Router latency.  We will put half the latency on input_latency
    # and half on output_latency
    router_latency = UnitAlgebra("100ns")
    input_latency = router_latency / ua_two
    output_latency = router_latency / ua_two

    # Link latency
    link_latency = UnitAlgebra("50ns")

    # Compute input buffer to be 3x roundtrip bandwidth delay product
    total_latency = link_latency + router_latency
    total_letency = total_latency * ua_three
    input_buffer_size = total_latency * link_bw

    # Minimum buffer size is 4kB, which is 2x the MTU size of the
    # firefly stack
    min_size = UnitAlgebra("4kB")
    if input_buffer_size < min_size:
        input_buffer_size = min_size

    #### Grab the default values for the firefly stack
    PlatformDefinition.setCurrentPlatform("firefly-defaults")

    #### Setup the network
    ## Set up the topology
    topo = topoDragonFly()
    topo.algorithm = ["ugal"]

    topo.hosts_per_router = 16
    topo.routers_per_group = args.group_size // topo.hosts_per_router
    topo.num_groups = args.num_groups
    topo.intergroup_links = args.group_size // args.num_groups
    if args.bw == 'half':
        topo.intergroup_links = topo.intergroup_links // 2
    if args.bw == 'quarter':
        topo.intergroup_links = topo.intergroup_links // 4

    print('System config:')
    print(f'  hosts:             {topo.getNumNodes()}')
    print(f'  hosts_per_router:  {topo.hosts_per_router}')
    print(f'  routers_per_group: {topo.routers_per_group}')
    print(f'  group_size:        {topo.routers_per_group*topo.hosts_per_router}')
    print(f'  intergroup_links:  {topo.intergroup_links}')
    print(f'  num_groups:        {topo.num_groups}')

    ## Set up the routers
    router = hr_router()
    router.link_bw = link_bw
    router.flit_size = "16B"
    router.xbar_bw = xbar_bw
    router.input_latency = input_latency
    router.output_latency = output_latency
    router.input_buf_size = input_buffer_size
    router.output_buf_size = input_buffer_size
    router.input_buf_size = input_buffer_size
    router.output_buf_size = input_buffer_size
    router.num_vns = 1
    router.xbar_arb = "merlin.xbar_arb_lru"

    topo.router = router
    topo.link_latency = link_latency

    # Get total number of nodes from toplogy object
    total_nodes = topo.getNumNodes()

    ## Define the LinkControl

    # Need to use ReorderLinkControl because we are using adaptive
    # routing and packets may get delivered out of order
    link_control = ReorderLinkControl()
    link_control.link_bw = link_bw
    link_control.input_buf_size = input_buffer_size
    link_control.output_buf_size = input_buffer_size

    #### Define the applications running on system
    jobs_list = []

    if app_name == "halo":
        # Figure out the size of the jobs
        max_ranks = (total_nodes) * 4 / num_jobs
        size = int(round( max_ranks ** (1. / 3)))
        # Make sure we didn't round up to something too big
        if size ** 3 > max_ranks:
            size -= 1

        # Size must be even because we're using 8 ranks per node
        if size % 2 == 1:
            size -= 1

        # Generate halo motif string
        work=args.work
        halo_string = f"Halo3D26 pex={size} pey={size} pez={size} nx={work} ny={work} nz={work} iterations=1 computetime=187200 fields_per_cell=8"


        for i in range(num_jobs):
            # create the ember job.  Parameters are:
            # (job_id, num_nodes, numCores = 1, nicsPerNode = 1)
            ep = EmberMPIJob(i, (size * size * size) // 8, 8, 2)
            ep.network_interface = link_control
            # define the motifs to run
            ep.addMotif("Init")
            for i in range(0,iterations):
                ep.addMotif(halo_string)
                ep.addMotif("Allreduce")

            ep.addMotif("Fini")
            # enable motifLog, which will print a log entry whenever a motif
            # starts or stops
            #ep.enableMotifLog("motiflog" + suffix)

            jobs_list.append(ep)

    elif args.app == "sweep":
        # Figure out the size of the jobs
        max_ranks = (total_nodes * 4 ) / num_jobs
        size = int(round( max_ranks ** (1. / 2)))
        # Make sure we didn't round up to something too big
        if size ** 2 > max_ranks:
            size -= 1

        # Size must be divisible by 4 because we're using 8 ranks per node
        if size % 2 == 1:
            size -= 1
        if size % 4 != 0:
            size -= 2

        # Generate sweep motif string
        sweep_string = "Sweep3D pex=%d pey=%d nx=8 ny=8 nz=60 kba=10 iterations=%d computetime=293 fields_per_cell=8"%(size,size,iterations)

        for i in range(num_jobs):
            # create the ember job.  Parameters are:
            # (job_id, num_nodes, numCores = 1, nicsPerNode = 1)
            ep = EmberMPIJob(i, (size * size) // 8, 8, 2)
            ep.network_interface = link_control
            # define the motifs to run
            ep.addMotif("Init")
            ep.addMotif(sweep_string)
            ep.addMotif("Fini")
            # enable motifLog, which will print a log entry whenever a motif
            # starts or stops
            #ep.enableMotifLog("motiflog" + suffix)

            jobs_list.append(ep)

    elif args.app == "fft":
        # Figure out the size of the jobs
        max_ranks = (total_nodes * 4 ) / num_jobs
        size = int(round( max_ranks ** (1. / 2)))
        # Make sure we didn't round up to something too big
        if size ** 2 > max_ranks:
            size -= 1

        # Size must be divisible by 4 because we're using 8 ranks per node
        if size % 2 == 1:
            size -= 1
        if size % 4 != 0:
            size -= 2

        for i in range(num_jobs):
            # create the ember job.  Parameters are:
            # (job_id, num_nodes, numCores = 1, nicsPerNode = 1)
            ep = EmberMPIJob(i, (size * size) // 8, 8, 2)
            print(i, (size*size)//8, 8, 2)
            ep.network_interface = link_control
            # define the motifs to run
            ep.addMotif("Init")
            ep.addMotif(f"FFT3D npRow={size} nx={args.work} ny={args.work} nz={args.work} iterations={iterations}")
            ep.addMotif("Fini")
            # enable motifLog, which will print a log entry whenever a motif
            # starts or stops
            #ep.enableMotifLog("motiflog" + suffix)

            jobs_list.append(ep)


    #### Create the system object and allocate jobs
    system = System()
    # Set the allocation block size to 2 because there are two NICs
    # per node and NICs on the same node are required to be allocated
    # to contiguous endpoint IDs
    system.allocation_block_size = 2
    system.topology = topo

    for ep in jobs_list:
        system.allocateNodes(ep,"random-linear", 2025) # seed = 2025

    system.build()

if __name__ == '__main__':
  ap = argparse.ArgumentParser()
  ap.add_argument('--num_groups', type=int, default=5,
                  help='Number of groups in the dragonfly network.')
  ap.add_argument('--group_size', type=int, default=512, choices=[512,256],
                  help='Size of a group in the network.')
  ap.add_argument('--work', type=int, default=60,
                  help='Dimension for Halo3D.')
  ap.add_argument('--bw', type=str, default='full', choices=['full','half','quarter'],
                  help='Bisection bandwidth')
  ap.add_argument('--app', type=str, choices=['halo', 'sweep', 'fft'],
                  help='Which app to run.')
  ap.add_argument('--jobs', type=int, default=4,
                  help='Number of jobs.')
  ap.add_argument('--iters', type=int, default=20,
                  help='Number of iterations of main motif in each job')
  args = ap.parse_args()
  main(args)
