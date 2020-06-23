# -*- coding: latin-1 -*-
import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging

#
# stereo_points
#

class stereo_points(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "Stereotactic points"
        self.parent.categories = ["Navigation"]
        self.parent.dependencies = []
        self.parent.contributors = ["Dorian Vogel (FHNW, LiU)"] # replace with "Firstname Lastname (Organization)"
        self.parent.helpText = u"""
This module allows entering target points in stereotactic coordinates and have them transformed in RAS space. This requires the use of the "Leksell Frame localization" first. Points are also transformed in the reference image ijk space and the image without ijk2ras transform can also be created.
"""
        #self.parent.helpText += self.getDefaultModuleDocumentationLink()
        self.parent.acknowledgementText = u"""
This file was originally developed by Dorian Vogel, (Fachhochschule Nordwestschweitz, Muttenz, Switzerland; Linköping University, Linköping, Sweden). Financial support: FHNW, SSF, VR.
"""

#
# stereo_pointsWidget
#

class stereo_pointsWidget(ScriptedLoadableModuleWidget):
    def setup(self):
        ScriptedLoadableModuleWidget.setup(self)


        stereoPointsAdd_collbtn = ctk.ctkCollapsibleButton()
        stereoPointsAdd_collbtn.text = 'Enter stereotactic points'
        self.layout.addWidget(stereoPointsAdd_collbtn)
        
        
        self.stereoPointsVBoxLayout = qt.QVBoxLayout(stereoPointsAdd_collbtn)
        self.stereoPointsFormLayout = qt.QFormLayout()
        self.pointTableView = slicer.qMRMLTableView()                
        
        self.referenceImage_selectionCombo = slicer.qMRMLNodeComboBox()
        self.referenceImage_selectionCombo.nodeTypes = ['vtkMRMLScalarVolumeNode']    
        self.referenceImage_selectionCombo.selectNodeUponCreation = True
        self.referenceImage_selectionCombo.noneEnabled = False
        self.referenceImage_selectionCombo.showHidden = False
        self.referenceImage_selectionCombo.showChildNodeTypes = False
        self.referenceImage_selectionCombo.setMRMLScene( slicer.mrmlScene )
        self.referenceImage_selectionCombo.setToolTip( "Select the image to transform the fiducials to:" )
        self.stereoPointsFormLayout.addRow('Reference image', self.referenceImage_selectionCombo)
        
        self.frameTransform_selectionCombo = slicer.qMRMLNodeComboBox()
        self.frameTransform_selectionCombo.nodeTypes = ['vtkMRMLTransformNode']    
        self.frameTransform_selectionCombo.selectNodeUponCreation = True
        self.frameTransform_selectionCombo.noneEnabled = False
        self.frameTransform_selectionCombo.showHidden = False
        self.frameTransform_selectionCombo.showChildNodeTypes = False
        self.frameTransform_selectionCombo.setMRMLScene( slicer.mrmlScene )
        self.frameTransform_selectionCombo.setToolTip( "Transformation obtained during the ICP frame registration" )
        self.stereoPointsFormLayout.addRow('Frame to image transform', self.frameTransform_selectionCombo)
        
        
        self.fiducialGroup_selectionCombo = slicer.qMRMLNodeComboBox()
        self.fiducialGroup_selectionCombo.nodeTypes = ['vtkMRMLMarkupsFiducialNode']    
        self.fiducialGroup_selectionCombo.selectNodeUponCreation = True
        self.fiducialGroup_selectionCombo.renameEnabled=True
        self.fiducialGroup_selectionCombo.noneEnabled = False
        self.fiducialGroup_selectionCombo.showHidden = False
        self.fiducialGroup_selectionCombo.showChildNodeTypes = False
        self.fiducialGroup_selectionCombo.setMRMLScene( slicer.mrmlScene )
        self.fiducialGroup_selectionCombo.baseName = 'Stereotactic_points'
        self.fiducialGroup_selectionCombo.setToolTip( "Select fiducial node for coordinates conversion" )
        self.stereoPointsFormLayout.addRow('Fiducial group', self.fiducialGroup_selectionCombo)
        
        self.stereoPointsVBoxLayout.addLayout(self.stereoPointsFormLayout)
        self.stereoPointsVBoxLayout.addWidget(self.pointTableView)
        
        self.NewPointHBox = qt.QHBoxLayout()
        
        self.nameField= qt.QLineEdit()
        self.nameField.setPlaceholderText('Add new point')
        self.NewPointHBox.addWidget(self.nameField)
        
        self.xLabel = qt.QLabel('X')
        self.xLabel.setAlignment(qt.Qt.AlignRight | qt.Qt.AlignVCenter)
        self.xField = qt.QDoubleSpinBox()
        self.xField.setMaximum(999.99)
        self.NewPointHBox.addWidget(self.xLabel)
        self.NewPointHBox.addWidget(self.xField)
        
        self.yLabel = qt.QLabel('Y')
        self.yLabel.setAlignment(qt.Qt.AlignRight | qt.Qt.AlignVCenter)
        self.yField = qt.QDoubleSpinBox()
        self.yField.setMaximum(999.99)
        self.NewPointHBox.addWidget(self.yLabel)
        self.NewPointHBox.addWidget(self.yField)
        
        self.zLabel = qt.QLabel('Z')
        self.zLabel.setAlignment(qt.Qt.AlignRight | qt.Qt.AlignVCenter)
        self.zField = qt.QDoubleSpinBox()
        self.zField.setMaximum(999.99)
        self.NewPointHBox.addWidget(self.zLabel)
        self.NewPointHBox.addWidget(self.zField)
        
        self.addBtn = qt.QPushButton('+')
        self.NewPointHBox.addWidget(self.addBtn)
        
        self.stereoPointsVBoxLayout.addLayout(self.NewPointHBox)
        
        self.disorient_btn = qt.QPushButton('Disorient ref image')
        self.disorient_btn.setToolTip("In order to use the ijk coordinates, the IJK2RAS transform will be removed from the reference image selected and a new volume will be created. This volume will be of no use in Slicer, but can be loaded in not medical imaging softwares (paraview, matlab...). This will also copy the coordsConversion table to a new name in case you want to save it.")
        self.stereoPointsVBoxLayout.addWidget(self.disorient_btn)
        
        self.referenceImage_selectionCombo.connect('currentNodeChanged(vtkMRMLNode*)', self.onReferenceImageSelectedChanged)
        self.frameTransform_selectionCombo.connect('currentNodeChanged(vtkMRMLNode*)', self.onFrameTransformSelectedChanged)
        self.fiducialGroup_selectionCombo.connect('currentNodeChanged(vtkMRMLNode*)', self.onFiducialSelectedChanged)
        self.disorient_btn.connect('clicked(bool)', self.onDisorientBtnClicked)
        
        self.addBtn.connect('clicked(bool)', self.onAddBtnClicked)

        self.fiducialNodesToCoordTables_id_tuples = list()
    
    ###################################################################################################
    # connections

    #########################################################################################################
    def onReferenceImageSelectedChanged(self, newNode):
        #coordTable = slicer.mrmlScene.GetNodesByName(self.fiducialGroup_selectionCombo.currentNode().GetName() + "_coordsConversion").GetItemAsObject(0)
        coordTable = slicer.mrmlScene.GetNodeByID(
            self.findMatchingNodeInIdTupleList(self.fiducialNodesToCoordTables_id_tuples,
                                               self.fiducialGroup_selectionCombo.currentNode().GetID()))
        self.updatePointsCoordsFromXYZ(coordTable, newNode, self.frameTransform_selectionCombo.currentNode())
        self.disorient_btn.setText('Disorient "'+newNode.GetName()+'"')
        
    def onFrameTransformSelectedChanged(self, newNode):
        #coordTable = slicer.mrmlScene.GetNodesByName(self.fiducialGroup_selectionCombo.currentNode().GetName() + "_coordsConversion").GetItemAsObject(0)
        coordTable = slicer.mrmlScene.GetNodeByID(
            self.findMatchingNodeInIdTupleList(self.fiducialNodesToCoordTables_id_tuples,
                                               self.fiducialGroup_selectionCombo.currentNode().GetID()))
        self.updatePointsCoordsFromXYZ(coordTable, self.referenceImage_selectionCombo.currentNode(), newNode)
        
    def onFiducialSelectedChanged(self, newNode):
        #print('selection changed !')
        if(type(newNode) == type(slicer.vtkMRMLMarkupsFiducialNode())):
            coordTableName = newNode.GetName() + "_coordsConversion"
        else:
            return
        #print('looking for '+coordTableName)
        
        if slicer.mrmlScene.GetNodesByName(coordTableName).GetNumberOfItems() == 0:
            #print('create new table')
            coordTable = slicer.vtkMRMLTableNode()
            coordTable.SetName(coordTableName)
            coordTable.SetLocked(True)
            for col in ['Marker', 'X', 'Y', 'Z', 'R', 'A', 'S', 'i', 'j', 'k']:
                c = coordTable.AddColumn()
                c.SetName(col)
            
            slicer.mrmlScene.AddNode(coordTable)
            # keep a map of the fiducialNode <-> TableNode couples
            self.fiducialNodesToCoordTables_id_tuples.append((newNode.GetID(), coordTable.GetID()))
            # add an observer for both nodes, whenever one is renamed, the other one is renamed as well
            coordTable.AddObserver(vtk.vtkCommand.ModifiedEvent, self.onCoordTableModified)
            newNode.AddObserver(vtk.vtkCommand.ModifiedEvent, self.onFiducialNodeModified)
        else:
            #print('found it !')
            coordTable = slicer.mrmlScene.GetNodesByName(coordTableName).GetItemAsObject(0)
        
        #first populate the table with the markers in the fiducialNode
        #self.fiducial2Table(coordTable, newNode)
        self.pointTableView.setMRMLTableNode(coordTable)
        self.pointTableView.setFirstRowLocked(True)
        self.pointTableView.show()
    
    def onCoordTableModified(self, updatedNode,eventType):
        matchingFiducial_nodeID = self.findMatchingNodeInIdTupleList(self.fiducialNodesToCoordTables_id_tuples, updatedNode.GetID())
        fiducialNode = slicer.mrmlScene.GetNodeByID(matchingFiducial_nodeID)
        fiducialNode.SetName(updatedNode.GetName().replace('_coordsConversion', ''))
    
    def onFiducialNodeModified(self, updatedNode, eventType):
        matchingCoordTable_nodeID = self.findMatchingNodeInIdTupleList(self.fiducialNodesToCoordTables_id_tuples, updatedNode.GetID())
        coordTable = slicer.mrmlScene.GetNodeByID(matchingCoordTable_nodeID)
        coordTable.SetName(updatedNode.GetName()+'_coordsConversion')
    
        
    def findMatchingNodeInIdTupleList(self, tupleList, search):
        #print('looking for '+str(search)+ ' in '+str(tupleList))
        return [j for j in [i for i in tupleList if search in i][0] if j != search][0]
        
    def onAddBtnClicked(self):
        xyzCoord = [self.xField.value,self.yField.value,self.zField.value]
        
        coordTable = slicer.mrmlScene.GetNodeByID(
            self.findMatchingNodeInIdTupleList(self.fiducialNodesToCoordTables_id_tuples,
                                               self.fiducialGroup_selectionCombo.currentNode().GetID()))
        #coordTable = slicer.mrmlScene.GetNodesByName(self.fiducialGroup_selectionCombo.currentNode().GetName() + "_coordsConversion").GetItemAsObject(0)
        
        self.addPointFromXYZ(coordTable, xyzCoord, self.nameField.text)
        
        self.table2Fiducial(coordTable, self.fiducialGroup_selectionCombo.currentNode())
        
        #self.fiducial2Table(coordTable, self.fiducialGroup_selectionCombo.currentNode())        
        
        self.nameField.setText('')
        self.xField.setValue(0.0)
        self.yField.setValue(0.0)
        self.zField.setValue(0.0)

    def onDisorientBtnClicked(self):
        import sitkUtils as siu
        refImg_itk = siu.PullVolumeFromSlicer(self.referenceImage_selectionCombo.currentNode().GetName())
        refImg_itk.SetDirection([1,0,0, 0,1,0, 0,0,1])
        refImg_itk.SetOrigin([0,0,0])
        siu.PushVolumeToSlicer(refImg_itk, name=self.referenceImage_selectionCombo.currentNode().GetName()+'_noOrient')
        
        coordTable = slicer.mrmlScene.GetNodeByID(
            self.findMatchingNodeInIdTupleList(self.fiducialNodesToCoordTables_id_tuples,
                                               self.fiducialGroup_selectionCombo.currentNode().GetID()))
        
        #clone the table node
        newTable = slicer.vtkMRMLTableNode()
        newTable.Copy(coordTable)
        newTable.SetName('stereotactic_points_'+self.referenceImage_selectionCombo.currentNode().GetName())
        slicer.mrmlScene.AddNode(newTable)


    def addPointFromXYZ(self, tableNode, xyz, label):
        r = tableNode.AddEmptyRow()
        tableNode.SetCellText(r, tableNode.GetColumnIndex('Marker'), label)
        tableNode.SetCellText(r, tableNode.GetColumnIndex('X'), '%.02f'%xyz[0])
        tableNode.SetCellText(r, tableNode.GetColumnIndex('Y'), '%.02f'%xyz[1])
        tableNode.SetCellText(r, tableNode.GetColumnIndex('Z'), '%.02f'%xyz[2])
        self.updatePointsCoordsFromXYZ(tableNode, self.referenceImage_selectionCombo.currentNode(), self.frameTransform_selectionCombo.currentNode())
        
    def updatePointsCoordsFromXYZ(self, tableNode, refImage, frameTransform):
        for iRow in range(tableNode.GetNumberOfRows()):
            xyz = [float(tableNode.GetCellText(iRow, tableNode.GetColumnIndex('X'))),
                   float(tableNode.GetCellText(iRow, tableNode.GetColumnIndex('Y'))),
                   float(tableNode.GetCellText(iRow, tableNode.GetColumnIndex('Z')))
                   ]
            
            [R,A,S] = self.XYZtoRAS(xyz)
            [i,j,k] = self.RASpatToIJK(self.RAStoRASpat(self.XYZtoRAS(xyz)))      
            tableNode.SetCellText(iRow, tableNode.GetColumnIndex('R'), '%.02f'%R)
            tableNode.SetCellText(iRow, tableNode.GetColumnIndex('A'), '%.02f'%A)
            tableNode.SetCellText(iRow, tableNode.GetColumnIndex('S'), '%.02f'%S)
            tableNode.SetCellText(iRow, tableNode.GetColumnIndex('i'), '%.02f'%i)
            tableNode.SetCellText(iRow, tableNode.GetColumnIndex('j'), '%.02f'%j)
            tableNode.SetCellText(iRow, tableNode.GetColumnIndex('k'), '%.02f'%k)

    def fiducial2Table(self, tableNode, fiducialNode):
        for iRow in range(tableNode.GetNumberOfRows()):
            tableNode.RemoveRow(0) #always remove the first
        for iFiducial in range(fiducialNode.GetNumberOfFiducials()):
            thisPosRAS = [0,0,0]
            fiducialNode.GetNthFiducialPosition(iFiducial, thisPosRAS)
            thisLabel = fiducialNode.GetNthFiducialLabel(iFiducial)
            
            r = tableNode.AddEmptyRow()
            tableNode.SetCellText(r, tableNode.GetColumnIndex('Marker'), thisLabel)
            tableNode.SetCellText(r, tableNode.GetColumnIndex('R'), '%.02f'%thisPosRAS[0])
            tableNode.SetCellText(r, tableNode.GetColumnIndex('A'), '%.02f'%thisPosRAS[1])
            tableNode.SetCellText(r, tableNode.GetColumnIndex('S'), '%.02f'%thisPosRAS[2])
    
    def table2Fiducial(self, tableNode, fiducialNode):
        fiducialNode.RemoveAllMarkups()
        
        for iRow in range(tableNode.GetNumberOfRows()):
            fiducialNode.AddPointToNewMarkup(vtk.vtkVector3d([float(tableNode.GetCellText(iRow, tableNode.GetColumnIndex('R'))),
                                                              float(tableNode.GetCellText(iRow, tableNode.GetColumnIndex('A'))),
                                                              float(tableNode.GetCellText(iRow, tableNode.GetColumnIndex('S'))),
                                                              ]),
                                            tableNode.GetCellText(iRow, tableNode.GetColumnIndex('Marker'))
                                            )
            fiducialNode.SetNthMarkupLocked(fiducialNode.GetNumberOfFiducials()-1, True)
    
            
    def XYZtoRAS(self, xyz):
        import numpy as np
        
        if slicer.mrmlScene.GetNodesByName('leksell2RAS').GetNumberOfItems() == 0:
            slicer.util.loadTransform(os.path.join(os.path.split(__file__)[0], 'Ressources/Leksell_Frame/leksell2RAS.h5'))
        
        leksell2ras = self.transformNode_to_numpy4x4(slicer.mrmlScene.GetNodesByName('leksell2RAS').GetItemAsObject(0))

        return np.dot(leksell2ras, np.array(xyz+[1])).tolist()[:3]
    
    def RAStoRASpat(self, xyz):
        import numpy as np
        #print(xyz)
        ras2patLeksell = self.transformNode_to_numpy4x4(self.frameTransform_selectionCombo.currentNode())
        
        return np.dot(ras2patLeksell, np.array(xyz+[1])).tolist()[:3]
    
    def RASpatToIJK(self, xyz):
        import numpy as np
        import sitkUtils as siu
        
        vol = siu.PullVolumeFromSlicer(self.referenceImage_selectionCombo.currentNode().GetName())
        IJKtoPatRAS = np.zeros([4,4])
        IJKtoPatRAS[:3,:3] = np.array(vol.GetDirection()).reshape([3,3])
        IJKtoPatRAS[:3,3] = np.array(vol.GetOrigin())
        IJKtoPatRAS[3,3]=1
        
        
        #vtkMat = vtk.vtkMatrix4x4()
        #self.referenceImage_selectionCombo.currentNode().GetIJKToRASDirectionMatrix(vtkMat)
        #IJKtoPatRAS = np.array([vtkMat.GetElement(i,j) for i in range(4)for j in range(4)]).reshape([4,4])
        #print(IJKtoPatRAS)
        
        ##################################################################################################################
        ########## WARNING We add the LPS2RAS matrix in between, this has been determined experimentally with the code:
        
        ########CT_mrml = slicer.mrmlScene.GetNodesByName('CTpreop_(CT)').GetItemAsObject(0)
        ########mat=vtk.vtkMatrix4x4()
        ########CT_mrml.GetIJKToRASDirectionMatrix(mat)
        ########CT_mrml = np.array([mat.GetElement(i,j) for i in range(4)for j in range(4)]).reshape([4,4])
        
        ########CT_itk = siu.PullVolumeFromSlicer('CTpreop_(CT)')
        ########CT_ijk2ras = np.zeros([4,4])
        ########CT_ijk2ras[:3,:3] = np.array(CT_itk.GetDirection()).reshape([3,3])
        ########CT_ijk2ras[:3,3] = np.array(CT_itk.GetOrigin())
        ########CT_ijk2ras[3,3]=1
        
        #########divide the twomatrices and round:
        ########np.dot(CT_ijk2ras, np.linalg.inv(CT_mrml))
        ##################################################################################################################
        
        LPS2RAS = np.array([-1,0,0,0, 0,-1,0,0, 0,0,1,0, 0,0,0,1]).reshape([4,4])
        
        #return np.dot(np.linalg.inv(IJKtoPatRAS), np.dot( np.linalg.inv(LPS2RAS), np.array(xyz+[1]))).tolist()[:3]
        return np.dot(np.linalg.inv(IJKtoPatRAS), np.dot(LPS2RAS, np.array(xyz+[1]))).tolist()[:3]

    
    def transformNode_to_numpy4x4(self, node):
        import numpy as np
        from vtk import vtkMatrix4x4
        vtkMat = vtkMatrix4x4()
        node.GetMatrixTransformFromWorld(vtkMat)
        
        return np.array([vtkMat.GetElement(i,j) for i in range(4)for j in range(4)]).reshape([4,4])
        


    # Refresh Apply button state
    #self.onSelect()
    
    ###################################################################################################
    #connection handler methods

    def cleanup(self):
        pass

    #def onSelect(self):
        #self.applyButton.enabled = self.referenceImage_selectionCombo.currentNode() and self.outputSelector.currentNode()

    #def onApplyButton(self):
        #logic = stereo_pointsLogic()
        #enableScreenshotsFlag = self.enableScreenshotsFlagCheckBox.checked
        #imageThreshold = self.imageThresholdSliderWidget.value
        #logic.run(self.referenceImage_selectionCombo.currentNode(), self.outputSelector.currentNode(), imageThreshold, enableScreenshotsFlag)

##
# stereo_pointsLogic
#

class stereo_pointsLogic(ScriptedLoadableModuleLogic):
    """This class should implement all the actual
    computation done by your module.    The interface
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

    def isValidInputOutputData(self, inputVolumeNode, outputVolumeNode):
        """Validates if the output is not the same as input
        """
        if not inputVolumeNode:
            logging.debug('isValidInputOutputData failed: no input volume node defined')
            return False
        if not outputVolumeNode:
            logging.debug('isValidInputOutputData failed: no output volume node defined')
            return False
        if inputVolumeNode.GetID()==outputVolumeNode.GetID():
            logging.debug('isValidInputOutputData failed: input and output volume is the same. Create a new volume for output to avoid this error.')
            return False
        return True

    def run(self, inputVolume, outputVolume, imageThreshold, enableScreenshots=0):
        """
        Run the actual algorithm
        """

        if not self.isValidInputOutputData(inputVolume, outputVolume):
            slicer.util.errorDisplay('Input volume is the same as output volume. Choose a different output volume.')
            return False

        logging.info('Processing started')

        # Compute the thresholded output volume using the Threshold Scalar Volume CLI module
        cliParams = {'InputVolume': inputVolume.GetID(), 'OutputVolume': outputVolume.GetID(), 'ThresholdValue' : imageThreshold, 'ThresholdType' : 'Above'}
        cliNode = slicer.cli.run(slicer.modules.thresholdscalarvolume, None, cliParams, wait_for_completion=True)

        # Capture screenshot
        if enableScreenshots:
            self.takeScreenshot('stereo_pointsTest-Start','MyScreenshot',-1)

        logging.info('Processing completed')

        return True


class stereo_pointsTest(ScriptedLoadableModuleTest):
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
        self.test_stereo_points1()

    def test_stereo_points1(self):
        """ Ideally you should have several levels of tests.    At the lowest level
        tests should exercise the functionality of the logic with different inputs
        (both valid and invalid).    At higher levels your tests should emulate the
        way the user would interact with your code and confirm that it still works
        the way you intended.
        One of the most important features of the tests is that it should alert other
        developers when their changes will have an impact on the behavior of your
        module.    For example, if a developer removes a feature that you depend on,
        your test should break so they know that the feature is needed.
        """

        self.delayDisplay("Starting the test")
        #
        # first, get some data
        #
        import SampleData
        SampleData.downloadFromURL(
            nodeNames='FA',
            fileNames='FA.nrrd',
            uris='http://slicer.kitware.com/midas3/download?items=5767')
        self.delayDisplay('Finished with download and loading')

        volumeNode = slicer.util.getNode(pattern="FA")
        logic = stereo_pointsLogic()
        self.assertIsNotNone( logic.hasImageData(volumeNode) )
        self.delayDisplay('Test passed!')
