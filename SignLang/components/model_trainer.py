import os,sys
import yaml

from SignLang.utils.main_utils import read_yaml_file

from SignLang.logger import logging
from SignLang.exception import CustomException

from SignLang.entity.config_entity import ModelTrainerConfig
from SignLang.entity.artifacts_entity import ModelTrainerArtifact



class ModelTrainer:
    def __init__(self, model_trainer_config: ModelTrainerConfig):
        self.model_trainer_config = model_trainer_config

    def initiate_model_trainer(self) -> ModelTrainerArtifact:
        logging.info("Entered initiate_model_trainer method of ModelTrainer class")

        try:
            # Unzipping data
            logging.info("Unzipping data")
            os.system("tar -xvf signlang.zip")  # Use tar for unzipping; replace if you have a different tool
            os.remove("signlang.zip")
            logging.info("Unzip successful")

            # Reading number of classes from YAML file
            with open("data.yaml", 'r') as stream:
                num_classes = str(yaml.safe_load(stream)['nc'])

            model_config_file_name = self.model_trainer_config.weight_name.split(".")[0]
            print(model_config_file_name)

            config = read_yaml_file(f"yolov5/models/{model_config_file_name}.yaml")
            config['nc'] = int(num_classes)

            with open(f'yolov5/models/custom_{model_config_file_name}.yaml', 'w') as f:
                yaml.dump(config, f)

            # Training the model
            os.system(f"cd yolov5 && python train.py --img 416 --batch {self.model_trainer_config.batch_size} --epochs {self.model_trainer_config.no_epochs} --data ../data.yaml --cfg ./models/custom_yolov5s.yaml --weights {self.model_trainer_config.weight_name} --name yolov5s_results --cache")

            # Copying the trained model weights
            os.system("copy yolov5\\runs\\train\\yolov5s_results\\weights\\best.pt yolov5\\")
            os.makedirs(self.model_trainer_config.model_trainer_dir, exist_ok=True)
            os.system(f"copy yolov5\\runs\\train\\yolov5s_results\\weights\\best.pt {self.model_trainer_config.model_trainer_dir}\\")

            # Removing directories and files
            os.system("rmdir /s /q yolov5\\runs")
            os.system("rmdir /s /q train")
            os.system("rmdir /s /q test")
            os.system("del data.yaml")

            # Creating and returning the model trainer artifact
            model_trainer_artifact = ModelTrainerArtifact(
                trained_model_file_path="yolov5/best.pt",
            )

            logging.info("Exited initiate_model_trainer method of ModelTrainer class")
            logging.info(f"Model trainer artifact: {model_trainer_artifact}")

            return model_trainer_artifact

        except Exception as e:
            logging.error(f"An error occurred: {e}")
            raise CustomException(e, sys)