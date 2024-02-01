from dotenv import load_dotenv
import os, sys, time, cv2
from array import array
from PIL import Image, ImageDraw
from matplotlib import pyplot as plt
import numpy as np
import azure.ai.vision as sdk

def main():
    global cv_client
    
    try:
        load_dotenv()
        ai_endpoint = os.getenv('VISION_URL')
        ai_key = os.getenv('VISION_KEY')

        cv_client = sdk.VisionServiceOptions(ai_endpoint, ai_key)

        # Get image
        if len(sys.argv) > 1:
            image_file = os.path.join('static', 'input', sys.argv[2] + '.jpg')
        
            # Analyze image
            if sys.argv[1] == 'analyse':
                analyse_image(image_file, cv_client)

            # Generate thumbnail
            # Not supported in australiaeast
            if sys.argv[1] == 'bgf':
                backgroundForeground(image_file, cv_client)
        else:
            image_file = os.path.join('static', 'input', 'street.jpg')
            analyse_image(image_file, cv_client)


    except Exception as ex:
        print(ex)


def analyse_image(image_file, cv_client):
    print('\nAnalyzing', image_file)

    # Specify features to be retrieved
    analysis_options = sdk.ImageAnalysisOptions()

    features = analysis_options.features = (
        # sdk.ImageAnalysisFeature.CAPTION |
        # sdk.ImageAnalysisFeature.DENSE_CAPTIONS |
        sdk.ImageAnalysisFeature.TAGS |
        sdk.ImageAnalysisFeature.OBJECTS |
        sdk.ImageAnalysisFeature.PEOPLE
    )


    # Get image analysis
    image = sdk.VisionSource(image_file)

    image_analyzer = sdk.ImageAnalyzer(cv_client, image, analysis_options)

    result = image_analyzer.analyze()

    if result.reason == sdk.ImageAnalysisResultReason.ANALYZED:
        # Not supported in australiaeast
        # # Get image captions
        # if result.caption is not None:
        #     print("\nCaption:")
        #     print(" Caption: '{}' (confidence: {:.2f}%)".format(result.caption.content, result.caption.confidence * 100))

        # # Get image dense captions
        # if result.dense_captions is not None:
        #     print("\nDense Captions:")
        #     for caption in result.dense_captions:
        #         print(" Caption: '{}' (confidence: {:.2f}%)".format(caption.content, caption.confidence * 100))

        # Get image tags
        if result.tags is not None:
            print("\nTags:")
            for tag in result.tags:
                print(" Tag: '{}' (confidence: {:.2f}%)".format(tag.name, tag.confidence * 100))

        # Get objects in the image
        if result.objects is not None:
            print("\nObjects in image:")

            # Prepare image for drawing
            image = Image.open(image_file)
            fig = plt.figure(figsize=(image.width/100, image.height/100))
            plt.axis('off')
            draw = ImageDraw.Draw(image)
            color = 'cyan'

            for detected_object in result.objects:
                # Print object name
                print(" {} (confidence: {:.2f}%)".format(detected_object.name, detected_object.confidence * 100))
                
                # Draw object bounding box
                r = detected_object.bounding_box
                bounding_box = ((r.x, r.y), (r.x + r.w, r.y + r.h))
                draw.rectangle(bounding_box, outline=color, width=3)
                plt.annotate(detected_object.name,(r.x, r.y), backgroundcolor=color)

            # Save annotated image
            plt.imshow(image)
            plt.tight_layout(pad=0)
            outputfile = os.path.join('static', 'output', 'objects.jpg')
            fig.savefig(outputfile)
            print('Results saved in', outputfile)

        # Get people in the image
        if result.people is not None:
            print("\nPeople in image:")

            # Prepare image for drawing
            image = Image.open(image_file)
            fig = plt.figure(figsize=(image.width/100, image.height/100))
            plt.axis('off')
            draw = ImageDraw.Draw(image)
            color = 'cyan'

            for detected_people in result.people:
                if detected_people.confidence > 0.9:
                    # Draw object bounding box
                    r = detected_people.bounding_box
                    bounding_box = ((r.x, r.y), (r.x + r.w, r.y + r.h))
                    draw.rectangle(bounding_box, outline=color, width=3)

                    # Return the confidence of the person detected
                    print(" {} (confidence: {:.2f}%)".format(detected_people.bounding_box, detected_people.confidence * 100))
                
            # Save annotated image
            plt.imshow(image)
            plt.tight_layout(pad=0)
            outputfile = os.path.join('static', 'output', 'analysed_' + image_file.split(os.sep)[-1])
            fig.savefig(outputfile)
            print('Results saved in', outputfile)


    else:
        error_details = sdk.ImageAnalysisErrorDetails.from_result(result)
        print("Analysis failed.")
        print("\tError reason: {}".format(error_details.reason))
        print("\tError code: {}".format(error_details.error_code))
        print("\tError message: {}".format(error_details.message))


def backgroundForeground(image_file, cv_client):
    print('\nRemove the background from the image or generate a foreground matte')

    image = sdk.VisionSource(image_file)

    analysis_options = sdk.ImageAnalysisOptions()

    # Set the image analysis segmentation mode to background or foreground
    analysis_options.segmentation_mode = sdk.ImageSegmentationMode.BACKGROUND_REMOVAL
        
    image_analyzer = sdk.ImageAnalyzer(cv_client, image, analysis_options)

    result = image_analyzer.analyze()

    if result.reason == sdk.ImageAnalysisResultReason.ANALYZED:
        image_buffer = result.segmentation_result.image_buffer
        print("Segmentation result:")
        print("\tOutput image buffer size (bytes) = {}".format(len(image_buffer)))
        print("\tOutput image height = {}".format(result.segmentation_result.image_height))
        print("\tOutput image width = {}".format(result.segmentation_result.image_width))

        outputcv2.imwrite(os.path.join('static', 'output', 'processed_' + image_file.split(os.sep)[-1]), image_buffer)


    else:
        error_details = sdk.ImageAnalysisErrorDetails.from_result(result)
        print("Analysis failed.")
        print("\tError reason: {}".format(error_details.reason))
        print("\tError code: {}".format(error_details.error_code))
        print("\tError message: {}".format(error_details.message))
        print("\tDid you set the computer vision endpoint and key?")



if __name__ == "__main__":
    main()