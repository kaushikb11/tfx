# Lint as: python2, python3
# Copyright 2019 Google LLC. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Helper class to start TFX training jobs on AI Platform."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from typing import Any, Dict, List, Text

import absl

from tfx import types
from tfx.components.base import base_executor
from tfx.components.trainer import executor as tfx_trainer_executor
from tfx.extensions.google_cloud_ai_platform import runner


# Keys to the items in custom_config passed as a part of exec_properties.
TRAINING_ARGS_KEY = 'ai_platform_training_args'
JOB_ID_KEY = 'ai_platform_training_job_id'


class Executor(base_executor.BaseExecutor):
  """Start a trainer job on Google Cloud AI Platform (GAIP)."""

  def Do(self, input_dict: Dict[Text, List[types.Artifact]],
         output_dict: Dict[Text, List[types.Artifact]],
         exec_properties: Dict[Text, Any]):
    """Starts a trainer job on Google Cloud AI Platform.

    Args:
      input_dict: Passthrough input dict for tfx.components.Trainer.executor.
      output_dict: Passthrough input dict for tfx.components.Trainer.executor.
      exec_properties: Mostly a passthrough input dict for
        tfx.components.Trainer.executor. custom_config.ai_platform_training_args
        and custom_config.ai_platform_training_job_id are consumed by this
        class.  For the full set of parameters supported by Google Cloud AI
        Platform, refer to
        https://cloud.google.com/ml-engine/docs/tensorflow/training-jobs#configuring_the_job

    Returns:
      None
    Raises:
      ValueError: if ai_platform_training_args is not in
      exec_properties.custom_config.
      RuntimeError: if the Google Cloud AI Platform training job failed.
    """
    self._log_startup(input_dict, output_dict, exec_properties)

    custom_config = exec_properties.get('custom_config', {})
    training_inputs = custom_config.get(TRAINING_ARGS_KEY)
    if training_inputs is None:
      err_msg = '\'%s\' not found in custom_config.' % TRAINING_ARGS_KEY
      absl.logging.error(err_msg)
      raise ValueError(err_msg)

    job_id = custom_config.get(JOB_ID_KEY)
    executor_class_path = '%s.%s' % (tfx_trainer_executor.Executor.__module__,
                                     tfx_trainer_executor.Executor.__name__)
    return runner.start_aip_training(input_dict, output_dict, exec_properties,
                                     executor_class_path, training_inputs,
                                     job_id)
