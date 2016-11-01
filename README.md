# PROJECT Deep Learning From Demonstrations
# AutoLab, UC Berkeley
Code for training an ABB YuMi robot to perform manipulation tasks from observing human demonstrators. 

## Policy Interface

This package provides a way to collect demonstrations (Kinesthic or Teleoperation) from a robot, train neural network policy primitives and string toward different manipulation tasks. 

### Installation
Step 1: Install the alan YuMi python interface on the client computer that will communicate with the YuMi:
```sh
$ python setup.py develop
```
```

