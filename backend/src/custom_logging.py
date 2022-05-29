import logging
import os
import time
from typing import Dict, List

import pymongo
from pymongo import MongoClient


DATABASE_NAME = os.getenv("GANSLIDER_LOG_DATABASE", "GANSLIDER_DB_DEFAULT")
DEBUGGING = os.environ.get('GANSLIDER_DEBUGGING', 'False').lower() in [
    'true', '1', 't']

print("Set log database to", DATABASE_NAME)


class Logger:
    def __init__(self, name):
        self.logger = logging.getLogger(name)
        sh = logging.StreamHandler()
        fmt = logging.Formatter("%(color)s%(levelname)-8s: %(message)s")
        sh.setFormatter(fmt)
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(sh)

        self.extra = {"color": "\033[0m"}

        try:
            self.client = MongoClient(host="mongodb", port=27017)
            self.db = self.client[DATABASE_NAME]
        except pymongo.error.ConnectionFailure as err:
            self.logger.warn("Failed to connect to mongo database. Continue without database...")

    def info(self, msg):
        self.logger.info(msg, extra=self.extra)

    def warn(self, msg):
        self.logger.warn(msg, extra=self.extra)

    def debug(self, msg):
        self.logger.debug(msg, extra=self.extra)

    def error(self, msg):
        self.logger.error(msg, extra={'color': '\033[91m'})

    def log_interaction(self, pid, psess_id, pstudy_id, sess_id, edits, seed, timestamp, sliderType, taskid, status):
        try:
            data = {
                "edits": edits,
                "seed": seed,
                "timestamp": timestamp,
                "pid": pid,
                "psess_id": psess_id,
                "pstudy_id": pstudy_id,
                "sess_id": sess_id,
                "sliderType": sliderType,
                "taskid": taskid,
                "status": status
            }
            if (DEBUGGING):
                self.debug(data)
            self.db.interactions.insert_one(data)
        except:
            self.error("Error while inserting document")
            self.error([pid, edits, seed, timestamp, taskid])

    def log_task_survey(self, surveyData, pid, psess_id, pstudy_id, sess_id):
        try:
            taskid = surveyData['taskid']

            likert = [{
                'taskid': taskid,
                'question': entry['question'],
                **dict(entry['scales']),
                "pid": pid,
                "psess_id": psess_id,
                "pstudy_id": pstudy_id,
                "sess_id": sess_id
            } for entry in surveyData['likert']]

            nasa_tlx = [{
                'taskid': taskid,
                "question": entry['question'],
                "answer": entry['answer'],
                "pid": pid,
                "psess_id": psess_id,
                "pstudy_id": pstudy_id,
                "sess_id": sess_id
            } for entry in surveyData['nasa_tlx']]

            if (DEBUGGING):
                self.debug(likert)
                self.debug(nasa_tlx)

            self.db.likert.insert_many(likert)
            self.db.nasa_tlx.insert_many(nasa_tlx)
        except:
            self.error("Error while inserting document")
            self.error([surveyData, pid])

    def log_final_survey(self, survey, pid, psess_id, pstudy_id, sess_id):
        try:
            payload = {
                **survey,
                "pid": pid,
                "psess_id": psess_id,
                "pstudy_id": pstudy_id,
                "sess_id": sess_id
            }
            if (DEBUGGING):
                self.debug(payload)

            self.db.final_survey.insert_one(payload)
        except:
            self.error("Error while inserting document")
            self.error([survey, pid])

    def log_task(self, task, pid, psess_id, pstudy_id, sess_id):
        try:
            payload = {
                **task,
                "pid": pid,
                "psess_id": psess_id,
                "pstudy_id": pstudy_id,
                "sess_id": sess_id,
            }
            if (DEBUGGING):
                self.debug(payload)

            self.db.task_status.insert_one(payload)
        except:
            self.error("Error while inserting document")
            self.error([task, pid])

    def log_config(self, config, pid, psess_id, pstudy_id, sess_id):
        try:
            payload = {'config': config}
            payload['pid'] = pid
            payload['psess_id'] = psess_id
            payload['pstudy_id'] = pstudy_id
            payload['sess_id'] = sess_id

            if (DEBUGGING):
                self.debug(payload)

            self.db.config_log.insert_one(payload)
        except Exception as e:
            self.error(["Error while inserting document", e])
            self.error([config, pid])

    def log_filmstrip_update(self, update, pid, psess_id, pstudy_id, sess_id):
        try:
            payload = update
            payload['pid'] = pid
            payload['psess_id'] = psess_id
            payload['pstudy_id'] = pstudy_id
            payload['sess_id'] = sess_id

            if (DEBUGGING):
                self.debug(payload)

            self.db.config_log.insert_one(payload)
        except Exception as e:
            self.error(["Error while inserting document", e])
            self.error([config, pid])