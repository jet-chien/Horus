# coding: utf-8
import time
from threading import Thread
import argparse
import pandas as pd
from pandas import DataFrame
import warnings

# JDE
from JDE.jde_start import jde_launch

# FaceRecog
from FaceRecog.Facer.shortcut import get_face_capturer, get_lmk_scanner, get_ag_face_recog
from FaceRecog.horus_fr_api import get_mf_data
from FaceRecog.horus_toolkit import UpdateTimer
from FaceRecog.horus_toolkit import get_face_recog_helper
from FaceRecog.horus_toolkit import sec_to_hms
from FaceRecog.horus_toolkit.db_tool import get_db_conn
from FaceRecog.Facer.ult import load_pkl

warnings.filterwarnings('ignore')

# >>>>>> listened variables >>>>>>
def get_latest_cus_df(cus_df_path='customer.pkl') -> DataFrame:
    # return load_pkl(cus_df_path)
    return cus_df_ls[0]

# <<<<<< listened variables <<<<<<


# >>>>>> re-id module >>>>>>
# TODO re-id entry-point
# <<<<<< re-id module <<<<<<


# >>>>>> face recognition module >>>>>>
def launch_face_recog():
    msg = '[FACE-RECOG][INFO] - face recog thread start.'
    print(msg)

    # const var
    member_table_name = 'member'
    customer_table_name = 'customer'
    listen_duration = 5  # minutes
    listen_duration *= 60

    # pre-work (about 4 sec)
    fr_db_conn = get_db_conn()
    face_capturer = get_face_capturer()
    lmk_scanner = get_lmk_scanner()
    ag_face_recog = get_ag_face_recog()
    mf_data = get_mf_data(fr_db_conn, member_table_name)
    fr_helper = get_face_recog_helper(face_capturer,
                                      lmk_scanner,
                                      ag_face_recog,
                                      mf_data,
                                      fr_db_conn,
                                      member_table_name,
                                      customer_table_name)

    # face recog work
    last_df = get_latest_cus_df()
    u_timer = UpdateTimer()

    work_flag = True
    while work_flag:
        # check update status
        latest_cus_df = get_latest_cus_df()
        if latest_cus_df.values.tolist() != last_df.values.tolist():
            # do face recognition
            fr_helper.recognize_df(latest_cus_df)

            last_df = latest_cus_df
            u_timer.reset()
            # work_flag = False  # only do 1 time

        else:
            # print('wait for update...')
            time.sleep(3)
            pass

        # check no update duration
        if u_timer.no_update_duration() > listen_duration:
            work_flag = False
            duration_str = sec_to_hms(u_timer.no_update_duration())
            msg = f"[FACE-RECOG][VITAL] - The database has not updated for {duration_str}, prepare to close job. \n"
            print(msg)

    msg = f"[FACE-RECOG][VITAL] - face recog thread finish."
    print(msg)


# <<<<<< face recognition module <<<<<<


# >>>>>> mot module >>>>>>
# TODO mot entry-point
# <<<<<< mot module <<<<<<


# >>>>>> fake mot module >>>>>>
def launch_jde(opt):
    jde_launch(opt)


# <<<<<< fake mot module <<<<<<


if __name__ == '__main__':
    cus_df_ls = [pd.DataFrame(columns=['id', 'cid', 'last_id', 'mid', 'customer_img', 'enter_time', 'leave_time', 'created_at', 'updated_at'])]

    parser = argparse.ArgumentParser(prog='demo.py')
    parser.add_argument('--cfg', type=str, default='JDE/cfg/yolov3_1088x608.cfg', help='cfg file path')
    parser.add_argument('--weights', type=str, default='JDE/weights/weight.pt', help='path to weights file')
    parser.add_argument('--iou-thres', type=float, default=0.5, help='iou threshold required to qualify as detected')
    parser.add_argument('--conf-thres', type=float, default=0.5, help='object confidence threshold')
    parser.add_argument('--nms-thres', type=float, default=0.4, help='iou threshold for non-maximum suppression')
    parser.add_argument('--min-box-area', type=float, default=200, help='filter out tiny boxes')
    parser.add_argument('--track-buffer', type=int, default=30, help='tracking buffer')
    parser.add_argument('--input-video', type=str, default='video_2.mp4', help='expected input root path')
    parser.add_argument('--output-format', type=str, default='video', choices=['video', 'text'],
                        help='Expected output format. Video or text.')
    parser.add_argument('--output-root', type=str, default='results', help='expected output root path')
    parser.add_argument('--customer', type=list, default=cus_df_ls)
    opt = parser.parse_args()
    mot_thread = Thread(target=launch_jde, args=(opt,))
    mot_thread.start()

    face_recog_thread = Thread(target=launch_face_recog)
    # face_recog_thread.start()