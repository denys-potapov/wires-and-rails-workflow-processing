#!/usr/bin/env python3

"""
Runner script. Define .env variables per .env.example and run e.g.

   python3 main.py
"""

import logging
import settings
from lib.logger import setup_logger
from lib.queue_operations import QueueOperations
from lib.kmeans_cluster_annotated_column_vertices import KmeansClusterAnnotatedColumnVertices
from panoptes_client import Panoptes
from redis import Redis
from rq import Queue

def run(log_level):
    """
    Query for completed subjects, calculate kmeans vertex centroids, fetch subject images, split
    columns by centroids, row segmentatino with Ocropy.
    """
    logger = setup_logger(settings.APP_NAME, 'log/kmeans_and_enqueue_completed_subjects.log',
                          log_level)
    logger.debug("Running Wires and Rails Workflow Processor")
    Panoptes.connect(username=settings.PANOPTES_USERNAME, password=settings.PANOPTES_PASSWORD)

    clusterer = KmeansClusterAnnotatedColumnVertices({
        'project_id': settings.PROJECT_ID,
        'workflow_id': settings.WORKFLOW_ID_DOCUMENT_VERTICES,
        'subject_set_id': settings.SUBJECT_SET_ID_DOCUMENT_VERTICES,
        'task_id': settings.TASK_ID_DOCUMENT_VERTICES_WORKFLOW
    })

    # Calculate vertex centroids
    vertex_centroids_by_subject = clusterer.calculate_vertex_centroids()

    logger.debug('Enqueueing the following subject centroids for image segmentation: %s',
                 str(vertex_centroids_by_subject))

    queue = Queue(connection=Redis(host=settings.REDIS_HOST))

    for subject_id, vertex_centroids in vertex_centroids_by_subject.items():
        queue.enqueue(QueueOperations.queue_new_subject_creation, subject_id, vertex_centroids)

# TODO SEQUENCE:
#
# [x] after kmeans clustering, shove the result into a queue (rq zB https://github.com/nvie/rq)
# [ ] write to Panoptes metadata saying we queued the subject for image processing
# [x] add rq, redis daeman starters to dockerfile
#  =  inside the rq arch
#     [x] move the vertical splitting logic in
#     [x] add the ocropy row segmenter
#     [ ] create new subjects w/ new cropped images w/ retained metadata
# [ ] revise such that we only pull & process subjects which haven't been retired / completed

if __name__ == '__main__':
    run(logging.DEBUG)