# Decription
StereoSlicer is an extension to [3DSlicer](https://www.slicer.org/) allowing to work with stereotactic arc settings (Leksell)
In substance, the module allows:
- To automatically detect N-shaped markers in stereotactic CT Images
- To generate the transform that will align the N-shaped markers so they "lay flat on the axial slicing plane", this has the effect of aligning the Leskell coordinate system with the coordinate system in slicer
- To place stereotactic points/trajectories with X,Y,Z,Ring,Arc settings
- Convert the postion of those points to patient space or image space

# Installation - Tutorial
A small [video tutorial](https://tube.switch.ch/videos/ZSYNlDwMgu) details the installation and use of StereoSlicer with an example case.

# Ideas for next features:

- observer on trajectory markers allowing to move then and update the coordinates in the table
- ~~possiblity to use trajectory to orient view (aka probe view)~~ <-- added by the probeView module
- 3d model of electrode
- 3d model of Leksell arc for more fancy viz
- remove dropdown menus for intermediate results to reduce usage intervension
