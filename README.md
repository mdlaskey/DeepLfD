# PROJECT ALAN
# AutoLab, UC Berkeley
Code for the ALAN project on YuMi.

## YuMi Python Interface

This package provides a python interface for control and communication with ABB's Yumi. Currently the interface is still undergoing development, so changes will occur to this repo. For best results please be on the newest commit of the control_stable branch before installing and using. 

### Installation
Step 1: Install the alan YuMi python interface on the client computer that will communicate with the YuMi:
```sh
$ python setup.py develop
```
Step 2: Upload SERVER_LEFT.mod and SERVER_RIGHT.mod under `src/alan/control/` to the left and right arms of YuMi through RobotStudio.
### Usage
Simple example to import and use the YuMi interface (make sure the YuMi is in Auto mode and has the server running):
```python
from alan.control import YuMiRobot
# starting the robot interface
y = YuMiRobot()
# getting the current pose of the right end effector
pose = y.right.get_pose()
# move right arm forward by 5cm using goto_pose
pose.position.x = pose.position.x + 50
y.right.goto_pose(pose)
# move right arm back by 5cm using move delta
y.right.goto_pose_delta((-50,0,0))
```

The control and RAPID server code is inspired by the [open-abb-driver](https://github.com/robotics/open_abb).