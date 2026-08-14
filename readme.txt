------INTRODUCTION------

This repository contains the core items of a Master Project implementation. The main goal was to reproduce in real condition a Federated Learning architecture proposed through a simulation in the literature in order to evaluate its potential and better understand how a federated system could be built.


------STRUCTURE------

A00057317_Axel_Marsacq_project_repository:.
├───demo
│   ├───final_demo_inference_training50rounds
│           final_demo_10_08_26_compressed.mp4
│           
├───docs
│       aggregator_loop.png
│       data_collection_system_schematic.pdf
│       global_system_schematic.pdf
│       twin_raspberry_system_schematic.pdf
│       
├───results
│   └───data_collection
│           AP_data_sample_home_1.csv
│           AP_data_sample_home_2.csv
│           
├───src
│   ├───home_assistant_AppDaemon
│   │       infer.py
│   │       train.py
│   │       
│   ├───second_raspberry_pi
│   │       nodeflloop.py
│   │       requirements.txt
│   │       
│   └───virtual_private_server
│           aggregator_fl_loop.py
│           requirements.txt
│           
└───testing
    ├───cluster_algo_eval
    │       clustertest.txt
    │       
    └───node_simulation
        │   node_fake.py
        │   proto_data.csv
        │   
        │       
        └───federated_training_simulation_with_two_fake_nodes_and_vps
                video.mp4


------COMPONENTS------

The repository is divided into 5 folders. 

The main one is -src, it contains all the python scipts needed to run the implementation. The three sub-folders separate the different scripts by the hardware on which they are running. 

The -demo folder regroups different demonstrations of the working system.

The -docs folder brings together implementation and design details.

The -testing folder contains containing data, code and tool which can be used to simulate some part of the system or evaluate it. (Need to create a python virtual environment with scikit-learn, numpy and matplotlib)

The -results folder merges data used in the Master project conference paper.


------USER GUIDE------

To execute the implementation the user will need three main components : a virtual private server with Ubuntu as operating system, a raspberry pi with the Home Assistant operating system and another raspberry pi with a Raspberry Pi operating system previously called Raspbian.

On the virtual private server, the user need to install the tensorflow and numpy packages to execute the aggregator_fl_loop.py python scripts when doing a Federated Training.

For the Home Assistant set up, the AppDaemon add-on need to be install alongside the Studio Code Server add-on. The two scripts train.py and infer.py need to be imported in AppDaemon as apps through the Studio Code Server UI. Then, the numpy package must be added into the configuration of AppDaemon. Finally, AppDaemon need to be started and the user starts either a training or an inference procedure by creating and using a start_training or making_inference helper button entity on the Home Assistant dashboard.

Python 3.11 needs to be installed on the second raspberry pi to enable the use of the package tensorflow. The numpy package must also be installed to enable the nodeflloop.py script to run on the raspberry. The systemd tool of ubuntu can be used to run the script at each boot the second raspberry.







