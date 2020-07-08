import pdb
def segment_zFrame(in_img, img_type='MR', withPlots=False):
    import SimpleITK as sitk
    import numpy as np
    
    
    from scipy.signal import butter, filtfilt
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        withPlots=False
    import math
    
    in_img_np = sitk.GetArrayFromImage(in_img)
    voxelCount = in_img_np.shape[0]*in_img_np.shape[1]*in_img_np.shape[2]

    hist_y, hist_x=np.histogram(in_img_np.flatten(), bins=int(in_img_np.max()/4))
 
    hist_x = hist_x[1:]
    
    #filter the histogram
    
    cumHist_y = np.cumsum(hist_y.astype(float))/voxelCount
    #we postulate that the background contain half of the voxels
    minThreshold_byCount = hist_x[np.where(cumHist_y>0.90)[0][0]]
    print("background threshold by count found: %d"%minThreshold_byCount)


    b,a =butter(2, 0.15, btype='low', analog=False)
    hist_y = filtfilt(b, a, hist_y)
    

    #then we look for minimas on the histogram
    hist_diff = np.diff(hist_y)
    
    #b,a =butter(2, 20/(.5*int(in_img_np.max()/8)), btype='low', analog=False)
    
    #hist_diff = filtfilt(b, a, hist_diff)
    
    
    hist_diff_zc = np.where(np.diff(np.sign(hist_diff))==2)[0].flatten()
    if withPlots: print(hist_x[hist_diff_zc])
    
    if img_type == 'MR':
        minThreshold_byVariation = hist_x[hist_diff_zc[hist_x[hist_diff_zc]>minThreshold_byCount][1]] #use the second minima after background (seems to work ok on t1)
        print("first maxima after background found: %d"%minThreshold_byVariation)
    elif img_type == 'CT':
        secondSpikeVal_intens = hist_x[np.where(hist_y == hist_y[hist_x>minThreshold_byCount].max())]
        #minThreshold_byVariation = hist_x[hist_diff_zc[hist_x[hist_diff_zc]>secondSpikeVal_intens]][0]
        minThreshold_byVariation_id = hist_diff_zc[hist_x[hist_diff_zc] > (minThreshold_byCount+100)][0]
        minThreshold_byVariation= hist_x[minThreshold_byVariation_id]
        print("first maxima after soft tissue found: %d"%minThreshold_byVariation)
    else:
        print('wrong image type passed !')
        return 0
    if withPlots:
        fig, ax=plt.subplots(2,1, sharex=True)
        ax[0].plot(hist_x, hist_y, label='intensity histogram')
        ax[1].plot(hist_x, cumHist_y, label='cumulative histogram')
        ax[1].axvline(x=minThreshold_byCount, ymin=0.0, ymax=1.0, color='r')

        ax[0].plot(hist_x[1:], hist_diff, label='derivative of intensity histogram')
        ax[0].plot(hist_x[hist_diff_zc], hist_diff[hist_diff_zc], linestyle='', marker='o', label="zero crossings of derivative of intensity histogram")

        ax[0].axvline(x=minThreshold_byCount, ymin=0.0, ymax=1.0, color='r')
        ax[0].axvline(x=minThreshold_byVariation, ymin=0.0, ymax=1.0, color='g')
        fig.legend()
        ax[0].grid()

    middleSlice = np.array(np.floor(np.array(in_img_np.shape)/2), dtype=int)

    thresh_img = in_img>minThreshold_byVariation

    if withPlots: 
        plt.figure()
        plt.imshow(sitk.GetArrayFromImage(thresh_img)[:,:,middleSlice[2]])


    # filter the labels by the size of their bounding boxes
    spacing_mm = in_img.GetSpacing()

    stats = sitk.LabelShapeStatisticsImageFilter()
    stats.SetComputeOrientedBoundingBox(True)
    connectedComponentImage = sitk.ConnectedComponent(thresh_img)
    
    stats.Execute(connectedComponentImage)
    
    print("%d labels were found before filter (id: size):"%(len(stats.GetLabels()) ))
    for i in stats.GetLabels():
        print('\t%d: %s'%(i, str(np.array(stats.GetBoundingBox(i)[3:])*spacing_mm)))
    #labelBBox_voxel = np.array([ stats.GetBoundingBox(l) for l in stats.GetLabels()])
    
    #labelBBox_size_mm = labelBBox_voxel[:,3:]*spacing_mm
    labelBBox_size_mm = np.array([ stats.GetOrientedBoundingBoxSize(l) for l in stats.GetLabels()])

    labelToKeep_mask = np.logical_and(np.sum(labelBBox_size_mm>120, axis=1)>0,
                                      np.sum(np.stack([labelBBox_size_mm[:,0]/labelBBox_size_mm[:,1],
                                                       labelBBox_size_mm[:,1]/labelBBox_size_mm[:,2],
                                                       labelBBox_size_mm[:,2]/labelBBox_size_mm[:,0]
                                                       ], axis=1)>10, axis=1)>0)
    
    #pdb.set_trace()
    connected_labelMap = sitk.LabelImageToLabelMap(connectedComponentImage)

    label_renameMap = sitk.DoubleDoubleMap()
    for i, toKeep in enumerate(labelToKeep_mask):
        if not toKeep:
            label_renameMap[i+1]=0
    newLabelMap = sitk.ChangeLabelLabelMap(connected_labelMap, label_renameMap)

    out_img = sitk.BinaryMorphologicalClosing(
                                        sitk.BinaryErode(
                                            sitk.BinaryDilate(sitk.LabelMapToLabel(newLabelMap)!=0, 1)
                                        , 1)
                                    , (1,1,1), sitk.sitkBall)

    if withPlots:
        plt.figure()
        plt.imshow(sitk.GetArrayFromImage(out_img)[:,:,middleSlice[2]]>0, cmap='gray')
    
    out_img = sitk.ConnectedComponent(out_img)
    
    stats.Execute(out_img)

    print("%d labels were found (id: size):"%(len(stats.GetLabels()) ))
    for i in stats.GetLabels():
        print('\t%d: %s'%(i, str(np.array(stats.GetBoundingBox(i)[3:])*spacing_mm)))

    if withPlots: plt.show()

    return out_img

def segment_zFrame_filesystem(in_file, out_file, img_type):
    import SimpleITK as sitk
    sitk.WriteImage(segment_zFrame(sitk.ReadImage(in_file), img_type, withPlots=True), out_file)
    
def segment_zFrame_slicer(inputVolume, outputVolume, img_type):
    import sitkUtils as siu
    try:
        import scipy
    except ImportError as e:
        slicer.util.pip_install('scipy')


    in_img = siu.PullVolumeFromSlicer(inputVolume)
    siu.PushVolumeToSlicer(segment_zFrame(in_img, img_type, withPlots=False), outputVolume)

if __name__ == "__main__":
    import argparse, os
    argParser = argparse.ArgumentParser()
    argParser.add_argument("-i", "--input_image", nargs=1, help="Stereotactic image.", required=True)
    argParser.add_argument("-o", "--output_image", nargs=1, help="Segmented stereotactic frame.", required=True)
    argParser.add_argument('-t', '--image_type', nargs=1, help="MR/CT", required=False)
    args = argParser.parse_args()
    segment_zFrame_filesystem(os.path.abspath(args.input_image[0]), os.path.abspath(args.output_image[0]), args.image_type[0])
    
