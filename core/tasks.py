import os
from celery import shared_task
from google.cloud import videointelligence
from .models import Video, VideoTag

@shared_task
def analyze_video_for_tags(video_id):
    # Set the path to Google Cloud credentials
    credentials_path = os.path.join(os.path.dirname(__file__), '..', 'crested-bloom-449817-m5-251ba2cdd0f1.json')
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path

    try:
        video = Video.objects.get(id=video_id)
        video_client = videointelligence.VideoIntelligenceServiceClient()

        # Read the video file content
        with video.video_file.open('rb') as f:
            input_content = f.read()

        # Set up the analysis features. We're asking for shot changes and labels.
        features = [
            videointelligence.Feature.SHOT_CHANGE_DETECTION,
            videointelligence.Feature.LABEL_DETECTION,
        ]

        # Run the analysis
        operation = video_client.annotate_video(
            request={"features": features, "input_content": input_content}
        )
        print(f"Waiting for operation for video {video.id} to complete...")
        result = operation.result(timeout=300)

        # Process and save the results (shot changes)
        shot_annotations = result.annotation_results[0].shot_annotations
        for shot in shot_annotations:
            start_time = shot.start_time_offset.total_seconds()
            end_time = shot.end_time_offset.total_seconds()
            VideoTag.objects.create(
                video=video,
                tag="Shot Change",
                start_time=start_time,
                end_time=end_time
            )

        # Process and save the results (labels)
        label_annotations = result.annotation_results[0].segment_label_annotations
        for label in label_annotations:
            if 'soccer' in label.entity.description or 'football' in label.entity.description:
                for segment in label.segments:
                    start_time = segment.segment.start_time_offset.total_seconds()
                    end_time = segment.segment.end_time_offset.total_seconds()
                    VideoTag.objects.create(
                        video=video,
                        tag=label.entity.description.capitalize(),
                        start_time=start_time,
                        end_time=end_time
                    )

        print(f"Analysis complete for video {video.id}")

    except Video.DoesNotExist:
        print(f"Video with ID {video_id} not found.")
    except Exception as e:
        print(f"An error occurred during video analysis: {e}")