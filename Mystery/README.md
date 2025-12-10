# SCC25-Mystery and IndySCC25-Mystery
The Mystery App for SCC and IndySCC at SC25

ACTS is a particle tracking toolkit for High Energy Physics experiments that reconstructs the trajectories of secondary particles produced by primary particle collisions inside of a detector.

It has a number of software dependencies on other packages. In order to facilitate building this project, we list the required sources and recommended versions below. Some of these packages, such as hepmc or dd4hep, depend on other packages in the list, so build order is important. There are some hints below as to how to configure the packages, but you should read their build instructions which are found on their repos for full configuration details.

- gcc: version 13 or 14
- cmake: something recent
- git-lfs: https://github.com/git-lfs/git-lfs/releases/download/v3.7.0/git-lfs-linux-amd64-v3.7.0.tar.gz
- boost: https://github.com/boostorg/boost.git **v1.86.0**
- eigen: https://gitlab.com/libeigen/eigen.git  **v3.4.0**
- nhlomann-json: https://github.com/nlohmann/json.git **v3.11.3**
- xerces-c: https://dlcdn.apache.org//xerces/c/3/sources/xerces-c-3.3.0.tar.gz
- tbb: https://github.com/oneapi-src/oneTBB  **v2022.2.0**
- pythia: https://pythia.org/download/pythia83/pythia8313.tgz
- root: https://github.com/root-project/root.git  **v6-34-04**
  - you can build without X11, vdt, xrootd and davix
- hepmc: https://gitlab.cern.ch/hepmc/HepMC3 **v3.3.1**
  - you can disable rootio, protobufio. enable interfaces and python
- lcio: https://github.com/iLCSoft/LCIO.git **v02-22-05**
- geant4: https://github.com/Geant4/geant4.git **v11.3.0**
  - enable GDML and multithreading
- dd4hep: https://github.com/AIDASoft/DD4hep.git **v01-32-01**
  - build with geant4, lcio, and xercesc enabled
- acts: https://github.com/acts-project/acts.git **v44.2.0**
  - build with python bindings, examples, dd4hep, pythia8, geant4, ODD

Code (root, geant, dd4hep, acts)  should be built with the C++20 standard

We recommend using the modules environment to setup important environment variables for each package such as **CMAKE_PREFIX_PATH**. There is an example module [file](modulefiles/xerces-c) for xerces-c in the modulefiles directory.

Running:
 - run your job using the **[full_chain_odd_sc25.py](full_chain_odd_sc25.py)** script. Place this in the `Examples/Scripts/Python` directory of ACTS source to run. After sourcing the `this_acts_with_deps.sh` script in your build directory, use the following command line options to run:
   - `python3 ../acts/Examples/Scripts/Python/full_chain_odd_sc25.py --ttbar --no-output-root --onlyWriteVertices`
 - there are other options available (see `--help` option) that you may find useful. Make sure however that you generate **ttbar** events at pile-up of **200**.
 - a single event takes between 5 and 20 seconds to process.
 - you will occasionally encounter FPEs while running. These are safe to ignore.

Testing:
 - run the job script (full_chain_odd_sc25.py) with the random number seed **12345** for one event. Compare the job's output file that containes the found vertices to the reference [files](reference) (check that your architecture matches).
- you should submit your test event output to the submission server under `Mystery/TestTask`

Your ultimate task is to process as many unique events as possible:
 - what is the maximum number of unique events you can process?
 - what is the total throughput (total events processed per second)?
 - **if you run multiple jobs, make sure each one starts with a unique random number seed**

Output file structure for grading:
- to grade your output, we will want to see the job logs (don't change the default logging level), and the vertices that ACTS finds. It will generate one file per event containing the reconstructed vertices, all in the same directory with names like event000001234-vertices.csv. You can change the name of the output directory via a command line option, which is what we suggest when running multiple jobs, otherwise the files will get overwritten.
- We will grade on three different things:
1. Test of Correctness
2. What is your maximum throughput (for a short run)? Run for a moderate amount of time (say 30 min to 1 hour) to get a good sample on all your hardware to determine what is the maximum number of events per second you can process.
3. How many unique events can you process in total? you can include the events in 2) as part of this

In your submission, create 3 directories.

1. Testing
   - just your vertex file for 1 event with 1 thread for rand seed **623819**
2. MaxThroughput
   - your job log, and the vertex files. 
   - If you ran more than one job, put each in a separate subdirectory with name jN, where N is the job number. Make sure we can tell that they were all run concurrently!
3. LongRun
   - your job log, and the vertex files.
   - If you ran more than one job, put each in a separate subdirectory with name jN, where N is the job number. make sure that each one is using a unique rand seed!


- you should submit your job logs and output files to the submission server under `Mystery/Task`. Write your answers to tasks 2) and 3) in a file called `ANSWERS.md` in that same directory. It should have 2 lines: for task 2), write your peak throughput as "events per second". For task 3) write the total number of unique events you processed.

IndySCC teams:
- use the ["Issues" tab of the IndySCC25-Mystery repository](https://github.com/StudentClusterCompetitionSC/IndySCC25-Mystery/issues) 
  to ask questions, and to browse already-asked questions

SCC teams:
- use the ["Issues" tab of the SCC25-Mystery repository](https://github.com/StudentClusterCompetitionSC/SCC25-Mystery/issues) 
  to ask questions, and to browse already-asked questions
