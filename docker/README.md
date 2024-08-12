# ReMIND2Reg Challenge - MICCAI 2024
Example docker containers for the ReMIND2Reg task of the Learn2Reg Challenge organized as part of MICCAI 2024. 
One docker container is expected for each type of MR sequences (2 in total).
The script simply predicts a zero displacement field.

## Build the Docker image
`Dockerfile_t1` and `Dockerfile_t2` contain all the information used to create the Docker container for the T1 and T2 sequences. 
Speficically, they both use the `continuumio/miniconda` image and installs additionnal Python libraries. 
Then, it automatically executes a dummy algorithm `src/run_inference_t1.py` or `src/run_inference_t2.py` on all the images located in `/input/` and write the diplacement fields in `/output/`.

To build the docker image for T1 scans:

```
docker build -f Dockerfile_t1 -t [your image] .
```

To build the docker image for T2 scans:

```
docker build -f Dockerfile_t2 -t [your image] .
```

## Docker commands
Containers submitted to the challenge will be run with the following commands:
```
docker run --rm -v [input directory]:/input/:ro -v [output directory]:/output -it [your image]
```

## Credits
This repository is based on the intructions provided for the MICCAI crossMoDA challenge. 
