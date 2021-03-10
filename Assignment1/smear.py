import cv2
import numpy as np
from glob import glob
from sys import argv , exit
from pathlib import Path
from os import mkdir

# Define a range for the area of the smear
minArea = 200
maxArea = 1000
# Define the frame size of the video
frameSize = (500, 500)

def main(src):
    path = str(src+"_results")
    mkdir(path)
    smear = False
    data= glob(src+"/*.jpg")
    # find mean of all pixel values of all images, append all the images in a list
    meanByPixel = np.zeros((500,500,3),np.float)
    pixel = []
    count, progress = 0 , 0
    for i in range(len(data)):
        # resize image to 500x500 and filter the image
        resize = cv2.resize(cv2.imread(data[i]),(500,500))
        pixel.append(resize)
        resize = cv2.medianBlur(resize,5)
        meanByPixel += resize
        progress = (i/len(data))*100
        if progress >=  count:
            print(str(count)+"% progress made in reading images")
            count += 10
    #  Save sample of filtered image
    cv2.imwrite(path+"/Filtered.jpg",cv2.medianBlur(pixel[-4],3))
    # Divide matrix by number of pictures to output the average pixel and save image
    meanByPixel /= len(data)
    cv2.imwrite(path+"/Mean.jpg", meanByPixel)
    # convert to grayscale and save image
    meanByPixel = np.array(np.round(meanByPixel),dtype=np.uint8)
    gray = cv2.cvtColor(meanByPixel, cv2.COLOR_BGR2GRAY)
    cv2.imwrite(path+"/gray.jpg",gray)
    # find ThresholdImage and save image
    thresholdImage = cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY, 105, 11)    
    cv2.imwrite(path+"/threshold.jpg", thresholdImage)
    # Use binary to form mask and save image
    mask = cv2.bitwise_not(thresholdImage)
    cv2.imwrite(path+"/MaskBeforeCheck.jpg",mask)
    # create blank image to represent mask of smears
    blank_image = np.zeros(shape=[512, 512, 3], dtype=np.uint8)
    print("Finding contours...\n")
    # find contours on mask image
    contours,_ = cv2.findContours(mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        # if contour is qualified as smear, draw a dontour arounf it.
        if cv2.contourArea(contour) > minArea and cv2.contourArea(contour) < maxArea:
            # draw contours around smear on original image
            for i in range(len(pixel)):
                pixel[i] = cv2.drawContours(pixel[i], contours=[contour], contourIdx=-1, color=(0, 0, 255), thickness=3)
            blank_image = cv2.drawContours(blank_image, contours=[contour], contourIdx=-1, color=(255, 255, 255), thickness=-1)
            smear = True
    cv2.imwrite(path+"/MaskAfterCheck.jpg",blank_image)
    # Save sample image and write video if smear is present
    if smear:
        cv2.imwrite(path+"/Smear_countoured.jpg",pixel[-4])
        out = cv2.VideoWriter(path+'/output_video.mp4',cv2.VideoWriter_fourcc(*'MP4V'), 60, frameSize)
        # Write image in video
        for img in pixel:
            out.write(img)
        out.release()
        # output video

    return smear

if __name__ == "__main__":
    path = Path('.')
    dirs = [str(e) for e in path.iterdir() if e.is_dir()]
    if len(argv) == 1:
        print("Please specify a dictionary")
        exit()
    if argv[1] not in dirs:
        print ("Directory "+ argv[1]+" not found")
        exit()
    print("Work in progress to find smear in " + argv[1] + "...\n")
    if main(argv[1]):
        print("Smear detected in " + argv[1]+". Please check folder created for results")
    else:
        print("No smear detected")
    