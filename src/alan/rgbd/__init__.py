'''
Alan Perception Module.
Authors: Jeff, Jacky
'''
import logging
from image import Image, ColorImage, DepthImage, IrImage, GrayscaleImage, BinaryImage
from camera_intrinsics import CameraIntrinsics
try:
    from kinect2_sensor import Kinect2PacketPipelineMode, Kinect2FrameMode, Kinect2RegistrationMode, Kinect2DepthMode, Kinect2Sensor, VirtualKinect2Sensor, load_images
    from camera_chessboard_registration import CameraChessboardRegister
except Exception:
    logging.warn("Cannot import kinect2_sensor!")
from depth_cnn_query_image import DepthToCNNQueryImage
try:
    from feature_extractors import CNNBatchFeatureExtractor
except Exception, e:
    logging.warn("Cannot import CNNBatchFeatureExtractor: \n{0}".format(str(e)))
from feature_matcher import FeatureMatcher, PointToPlaneFeatureMatcher
from registration import IterativeRegistrationSolver, PointToPlaneICPSolver, RegistrationResult
from object_render import ObjectRender, QueryImageBundle, RenderMode
from video_recorder import VideoRecorder
from opencv_camera_sensor import OpenCVCameraSensor

__all__ = ['Image', 'ColorImage', 'DepthImage', 'IrImage', 'GrayscaleImage',
          'Kinect2PacketPipelineMode', 'Kinect2FrameMode', 'Kinect2RegistrationMode',
          'Kinect2DepthMode', 'Kinect2Sensor',
          'CameraIntrinsics',
          'DepthToCNNQueryImage',
          'CNNBatchFeatureExtractor',
          'FeatureMatcher',
          'PointToPlaneFeatureMatcher',
          'IterativeRegistrationSolver',
          'PointToPlaneICPSolver',
          'RegistrationResult',
          'VideoRecorder',
          'CameraChessboardRegister',
          'OpenCVCameraSensor',
]
