cmake_minimum_required(VERSION 3.5)

project(StereoSlicer)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "https://github.com/IM2Neuroing/SlicerStereotactic.git")
set(EXTENSION_CATEGORY "Navigation")
set(EXTENSION_CONTRIBUTORS "Dorian Vogel (FHNW (CH), LiU (SE)), Marc Jermann (FHNW (CH))")
set(EXTENSION_DESCRIPTION "An extension to use stereotactic arc settings in slicer")
set(EXTENSION_ICONURL "https://raw.githubusercontent.com/IM2Neuroing/SlicerStereotactic/master/StereoSlicer.png")
set(EXTENSION_SCREENSHOTURLS "https://raw.githubusercontent.com/IM2Neuroing/SlicerStereotactic/master/resources/Images/Screenshot_02_StereotacticTrajectories.png")
set(EXTENSION_DEPENDS "NA") # Specified as a space separated string, a list or 'NA' if any

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(find_zFrame)
add_subdirectory(stereo_points)
add_subdirectory(probeView)

## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})
