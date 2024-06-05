The two folders each contain the source code for the python and unity implementation. 

For starting the python application run main.py in a python environment.

******************NOTES************************

Before you begin:

# Downloaded the correct unity version in order to avoid version conflicts

# teslasuit_newapi branch is not compatible with the master branch. These are two seperate projects doing the same thing.

# This project currently has
- Animate character using tesla suit
- Save rotation (quaternion) and/or rotation & position (vector3) data
- Extract and save them using a json format
- Replay the data
- Send the rotation and position data to python via python client

# This project currently lacks
- Determining the accuracy of trainings (python side)
- Give a feedback accordingly (python side)

# Steps to work with this Project. In general, LFS is crucial to work with Unity since some most files are larger than 10 mb and some larger than 100 mb. 

0- git lfs install
1- git clone repository, teslasuit_newapi branch
2- git lfs fetch -all
3- git lfs pull
4- Open the project in Unity, 
check Project Settings>Player> Configuration>API Comp Level set to -NET 4.x
5- Unity shouldn't throw unknown errors now.
6- Disable auto jump detector of suit (it causes wrong behaviours)
	- ProgramData/Teslasuit/teslasuit_api.config.xml
	- Set true in the following line: <without_jumps type="bool">true</without_jumps>

# Take Note
0- There are some changes in other packages, eg TS. Those changes have been marked with   //* For an example TsHumanAnimator.cs
1- "Scenes/MotionCaptureCaptureScene" is the scene where changes have been made.
2- In order to work with Json.Net it needs to be downloaded and imported from asset store

https://assetstore.unity.com/packages/tools/input-management/json-net-for-unity-11347

3-If the console still throw errors it is either a gizmo problem or python client problem.
if it is gizmos- ignore. If it is python, disable Datagateway component and try again. If it
still doesnt work go to "Assets/Plugins" there should be two plugins AsyncIO
and NetMq. They are responsible for python communication as well. Check if they are there.
If not, refer to the original thesis papers. Steps to use them are explained there.

4- Due to Unity's internal 3D Object workflow, the blender version installed in local computers
have problems reading the fbx files. This causes the gameobjects to lose their mesh data and become invisible.
If that occurs to you visit https://github.com/keijiro/KinoBinary/blob/master/Assets/Standard%20Assets/Characters/ThirdPersonCharacter/Models/Ethan.fbx
and download the fbx file. Import it back to project and restore the missing Ethan mesh data.


***************************************************** 
