import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging
import numpy as np

#
# Zframe_raster
#

class Zframe_raster(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "Zframe_raster" # TODO make this more human readable by adding spaces
    self.parent.categories = ["Examples"]
    self.parent.dependencies = []
    self.parent.contributors = ["John Doe (AnyWare Corp.)"] # replace with "Firstname Lastname (Organization)"
    self.parent.helpText = """
This is an example of scripted loadable module bundled in an extension.
It performs a simple thresholding on the input volume and optionally captures a screenshot.
"""
    self.parent.helpText += self.getDefaultModuleDocumentationLink()
    self.parent.acknowledgementText = """
This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc.
and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
""" # replace with organization, grant and thanks.

#
# Zframe_rasterWidget
#

class Zframe_rasterWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)

    # Instantiate and connect widgets ...

    #
    # Parameters Area
    #
    parametersCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersCollapsibleButton.text = "Parameters"
    self.layout.addWidget(parametersCollapsibleButton)

    # Layout within the dummy collapsible button
    parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)

    #
    # input volume selector
    #
    self.inputSelector = slicer.qMRMLNodeComboBox()
    self.inputSelector.nodeTypes = ["vtkMRMLModelNode"]
    self.inputSelector.selectNodeUponCreation = True
    self.inputSelector.addEnabled = False
    self.inputSelector.removeEnabled = False
    self.inputSelector.noneEnabled = False
    self.inputSelector.showHidden = False
    self.inputSelector.showChildNodeTypes = False
    self.inputSelector.setMRMLScene( slicer.mrmlScene )
    self.inputSelector.setToolTip( "Pick the ZFrame mesh." )
    parametersFormLayout.addRow("ZFrame: ", self.inputSelector)

    #
    # moving volume selector
    #
    self.movingImgSelector = slicer.qMRMLNodeComboBox()
    self.movingImgSelector.nodeTypes = ["vtkMRMLScalarVolumeNode"]
    self.movingImgSelector.selectNodeUponCreation = True
    self.movingImgSelector.addEnabled = True
    self.movingImgSelector.removeEnabled = True
    self.movingImgSelector.noneEnabled = True
    self.movingImgSelector.showHidden = False
    self.movingImgSelector.showChildNodeTypes = False
    self.movingImgSelector.setMRMLScene( slicer.mrmlScene )
    self.movingImgSelector.setToolTip( "Pick the moving image to the algorithm." )
    parametersFormLayout.addRow("Moving Volume: ", self.movingImgSelector)

        #
    # output volume selector
    #
    self.outputSelector = slicer.qMRMLNodeComboBox()
    self.outputSelector.nodeTypes = ["vtkMRMLScalarVolumeNode"]
    self.outputSelector.selectNodeUponCreation = True
    self.outputSelector.addEnabled = True
    self.outputSelector.removeEnabled = True
    self.outputSelector.renameEnabled = True
    self.outputSelector.noneEnabled = False
    self.outputSelector.showHidden = False
    self.outputSelector.showChildNodeTypes = False
    self.outputSelector.setMRMLScene( slicer.mrmlScene )
    self.outputSelector.setToolTip( "Pick the output to the algorithm." )
    parametersFormLayout.addRow("Output Volume: ", self.outputSelector)

    #
    # Apply Button
    #
    self.applyButton = qt.QPushButton("Apply")
    self.applyButton.toolTip = "Run the algorithm."
    self.applyButton.enabled = False
    parametersFormLayout.addRow(self.applyButton)

    # connections
    self.applyButton.connect('clicked(bool)', self.onApplyButton)
    self.inputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    self.movingImgSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    self.outputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    # Add vertical spacer
    self.layout.addStretch(1)

    # Refresh Apply button state
    self.onSelect()

  def cleanup(self):
    pass

  def onSelect(self):
    self.applyButton.enabled = self.inputSelector.currentNode() and self.movingImgSelector.currentNode() and self.outputSelector.currentNode()

  def onApplyButton(self):
    logic = Zframe_rasterLogic()
    logic.run(self.inputSelector.currentNode()
              , self.movingImgSelector.currentNode()
              , self.outputSelector.currentNode()
              )

#
# Zframe_rasterLogic
#

class Zframe_rasterLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def hasImageData(self,volumeNode):
    """This is an example logic method that
    returns true if the passed in volume
    node has valid image data
    """
    if not volumeNode:
      logging.debug('hasImageData failed: no volume node')
      return False
    if volumeNode.GetImageData() is None:
      logging.debug('hasImageData failed: no image data in volume node')
      return False
    return True

  def isValidInputOutputData(self, inputVolumeNode, movingVolumeNode, outputVolumeNode):
    """Validates if the output is not the same as input
    """
    if not inputVolumeNode:
      logging.debug('isValidInputOutputData failed: no input volume node defined')
      return False
    if not movingVolumeNode:
      logging.debug('isValidInputOutputData failed: no output volume node defined')
      return False
    if inputVolumeNode.GetID()==movingVolumeNode.GetID():
      logging.debug('isValidInputOutputData failed: input and output volume is the same. Create a new volume for output to avoid this error.')
      return False
    return True

  def run(self, inputMesh, movingVolume, outputVolume):
    """
    Run the actual algorithm
    """

    if not self.isValidInputOutputData(inputMesh, movingVolume, outputVolume):
      slicer.util.errorDisplay('Input volume is the same as output volume. Choose a different output volume.')
      return False

    logging.info('Processing started')

    meshBounds = (np.array(inputMesh.GetPolyData().GetBounds())*1.5).tolist()
    logging.info("bounds: %s"%str(meshBounds))
    mvSpacing = movingVolume.GetSpacing()

    rasterExtent = [0, int(round((abs(meshBounds[0])+abs(meshBounds[1]))/mvSpacing[0])),
                    0, int(round((abs(meshBounds[2])+abs(meshBounds[3]))/mvSpacing[1])),
                    0, int(round((abs(meshBounds[4])+abs(meshBounds[5]))/mvSpacing[2]))
                    ]
    rasterOrigin = [-rasterExtent[2*i+1]*mvSpacing[i]/2 for i in range(3)] 
    logging.info("Extent: %s"%str(rasterExtent))
    #movingVolume.GetBounds(movingImgBounds)
    logging.info('spacing %s'%str(movingVolume.GetSpacing()))

    refImage=vtk.vtkImageData()
    refImage.SetSpacing(mvSpacing)
    refImage.SetExtent(rasterExtent)
    refImage.SetOrigin(rasterOrigin)
    refImage.AllocateScalars(vtk.VTK_UNSIGNED_CHAR, 1)

    poly2stencil = vtk.vtkPolyDataToImageStencil()
    poly2stencil.SetInputData(inputMesh.GetPolyData())
    poly2stencil.SetOutputOrigin(rasterOrigin)
    poly2stencil.SetOutputSpacing(mvSpacing)
    poly2stencil.SetOutputWholeExtent(rasterExtent)
    poly2stencil.Update()

    imageStencil= vtk.vtkImageStencil()
    imageStencil.SetInputData(refImage)
    imageStencil.SetStencilConnection(poly2stencil.GetOutputPort())
    imageStencil.ReverseStencilOn()
    imageStencil.SetBackgroundValue(255)
    imageStencil.Update()

    refImage.ShallowCopy(imageStencil.GetOutput())
    refImage.SetSpacing([1.0,1.0,1.0])
    refImage.SetOrigin([0.0,0.0,0.0])

    outputVolume.SetAndObserveImageData(refImage)

    ijkToRas = vtk.vtkMatrix4x4()
    for i,val in enumerate([1, 0, 0, rasterOrigin[0],
                            0, 1, 0, rasterOrigin[1],
                            0, 0, 1, rasterOrigin[2],
                            0,0,1, 0]):
        ijkToRas.SetElement(int(i/4), i%4, val)

    logging.info(ijkToRas)
    outputVolume.SetIJKToRASMatrix(ijkToRas)
    outputVolume.SetSpacing(movingVolume.GetSpacing()) # WARNING: SetSpacing HAS TO BE after SetIJKToRASMatrix

    logging.info('Processing completed')

    return True


class Zframe_rasterTest(ScriptedLoadableModuleTest):
  """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_Zframe_raster1()

  def test_Zframe_raster1(self):
    """ Ideally you should have several levels of tests.  At the lowest level
    tests should exercise the functionality of the logic with different inputs
    (both valid and invalid).  At higher levels your tests should emulate the
    way the user would interact with your code and confirm that it still works
    the way you intended.
    One of the most important features of the tests is that it should alert other
    developers when their changes will have an impact on the behavior of your
    module.  For example, if a developer removes a feature that you depend on,
    your test should break so they know that the feature is needed.
    """

    self.delayDisplay("Starting the test")
    #
    # first, get some data
    #
    import urllib
    downloads = (
        ('http://slicer.kitware.com/midas3/download?items=5767', 'FA.nrrd', slicer.util.loadVolume),
        )

    for url,name,loader in downloads:
      filePath = slicer.app.temporaryPath + '/' + name
      if not os.path.exists(filePath) or os.stat(filePath).st_size == 0:
        logging.info('Requesting download %s from %s...\n' % (name, url))
        urllib.urlretrieve(url, filePath)
      if loader:
        logging.info('Loading %s...' % (name,))
        loader(filePath)
    self.delayDisplay('Finished with download and loading')

    volumeNode = slicer.util.getNode(pattern="FA")
    logic = Zframe_rasterLogic()
    self.assertIsNotNone( logic.hasImageData(volumeNode) )
    self.delayDisplay('Test passed!')
