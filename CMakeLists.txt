cmake_minimum_required(VERSION 3.5)

project(StereoSlicer)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "http://slicer.org/slicerWiki/index.php/Documentation/Nightly/Extensions/StereoSlicer")
set(EXTENSION_CATEGORY "Navigation")
set(EXTENSION_CONTRIBUTORS "Dorian Vogel (FHNW (CH), LiU (SE))")
set(EXTENSION_DESCRIPTION "This is an example of a simple extension")
set(EXTENSION_ICONURL "http://www.example.com/Slicer/Extensions/StereoSlicer.png")
set(EXTENSION_SCREENSHOTURLS "http://www.example.com/Slicer/Extensions/StereoSlicer/Screenshots/1.png")
set(EXTENSION_DEPENDS "NA") # Specified as a space separated string, a list or 'NA' if any

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(find_zFrame)
add_subdirectory(stereo_points)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})
