# Decription

StereoSlicer is an extension to [3DSlicer](https://www.slicer.org/) allowing to work with stereotactic arc settings (for now only Leksell).

This was presented as ePoster at ESSFN 2021 in Marseille (FR) https://doi.org/10.1159/000520618.

In substance, the module allows:

- To automatically detect N-shaped markers in stereotactic CT Images
- To generate the transform that will align the N-shaped markers so they "lay flat on the axial slicing plane", this has the effect of aligning the Leskell coordinate system with the coordinate system in slicer ![Frame Localization](resources/Images/Screenshot_01_FrameLocalization.png?raw=true "Frame Localization")

- To place stereotactic points/trajectories with X,Y,Z,Ring,Arc settings. ![Stereotactic Trajectories](resources/Images/Screenshot_02_StereotacticTrajectories.png?raw=true "Stereotactic Trajectories")

- Convert the postion of those points to patient space or image space ![Probe View](resources/Images/Screenshot_03_ProbeView.png?raw=true "Probe View")

# Installation - Tutorial

A small [video tutorial](https://tube.switch.ch/videos/ZSYNlDwMgu) details the installation and use of StereoSlicer with an example case.
