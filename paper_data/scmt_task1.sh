#!/usr/bin/env bash

#CUDA_VISIBLE_DEVICES=0,1 python single_channel_multi_task_cls.py --root ../data/kaggle/512 --traincsv ../data/kaggle/train_multi.csv --valcsv ../data/kaggle/val_multi.csv --testcsv ../data/kaggle/test_bin.csv --model rsn34 --batch 64 --workers 8 --epoch 100 --display 50

#CUDA_VISIBLE_DEVICES=0,1 python single_channel_multi_task_cls.py --root ../data/dme/512 --traincsv ../data/dme/train_multi.csv --valcsv ../data/dme/val_multi.csv --testcsv ../data/dme/test_bin.csv --model rsn34 --batch 64 --workers 8 --epoch 100 --display 50

#CUDA_VISIBLE_DEVICES=0,1 python single_channel_multi_task_cls.py --root ../data/kaggle/512 --traincsv ../data/kaggle/train_multi.csv --valcsv ../data/kaggle/val_multi.csv --testcsv ../data/kaggle/val_multi.csv --model rsn34 --batch 32 --workers 8 --epoch 100 --display 50 --phase test --crop 512 --size 512 --weight /home/weidong/code/github/DiabeticRetinopathy_solution/paper_data/output/kaggle_multi_task_cls_train_20170911155819_rsn34_multi_task/kaggle_multi_task_cls_dr_rsn34_015_best.pth

#CUDA_VISIBLE_DEVICES=0,1,2,3 python single_channel_multi_task_cls.py --root ../data/zhizhen_new/LabelImages/512 --traincsv ../data/zhizhen_new/LabelImages/train_multi.csv --valcsv ../data/zhizhen_new/LabelImages/val_multi.csv --testcsv ../data/zhizhen_new/LabelImages/test_multi.csv --model rsn34 --batch 64 --workers 8 --epoch 100 --display 50

#CUDA_VISIBLE_DEVICES=0,1,2,3 python single_channel_multi_task_cls.py --root ../data/zhizhen_new/LabelImages/512 --traincsv ../data/zhizhen_new/LabelImages/train_multi.csv --valcsv ../data/zhizhen_new/LabelImages/val_multi.csv --testcsv ../data/zhizhen_new/LabelImages/data_multi.csv --model rsn34 --batch 32 --workers 8 --epoch 100 --display 50 --crop 512 --size 512 --weight ./kaggle_multi_task_cls_dr_rsn34_012_best.pth --phase test

#CUDA_VISIBLE_DEVICES=0,1 python single_channel_multi_task_cls.py --root ../data/dme/512 --traincsv ../data/dme/train_multi.csv --valcsv ../data/dme/val_multi.csv --testcsv ../data/dme/train_multi.csv --model rsn34 --batch 32 --workers 8 --epoch 100 --display 50 --crop 512 --size 512 --weight ./output/kaggle_multi_task_cls_train_20170911202411_rsn34_multi_task/kaggle_multi_task_cls_dr_rsn34_021_best.pth --phase test

#CUDA_VISIBLE_DEVICES=0,1 python single_channel_multi_task_cls.py --root ../data/kaggle/512 --traincsv ../data/kaggle/train_multi.csv --valcsv ../data/kaggle/val_multi.csv --testcsv ../data/kaggle/train_multi.csv --model rsn34 --batch 32 --workers 8 --epoch 100 --display 50 --crop 512 --size 512 --weight ./output/kaggle_multi_task_cls_train_20170911202411_rsn34_multi_task/kaggle_multi_task_cls_dr_rsn34_021_best.pth --phase test


#CUDA_VISIBLE_DEVICES=0,1,2,3 python single_channel_multi_task_cls.py --root ../data/zhizhen_new/LabelImages/512 --traincsv ../data/zhizhen_new/LabelImages/train_multi.csv --valcsv ../data/zhizhen_new/LabelImages/val_multi.csv --testcsv ../data/zhizhen_new/LabelImages/data_multi.csv --model rsn34 --batch 200 --workers 8 --epoch 150 --display 50 --crop 448 --size 512

#CUDA_VISIBLE_DEVICES=0,1 python single_channel_multi_task_cls.py --root ../data/kaggle/512 --traincsv ../data/kaggle/train_multi.csv --valcsv ../data/kaggle/val_multi.csv --testcsv ../data/kaggle/test_multi.csv --model dsn121 --batch 8 --workers 4 --epoch 100 --display 50

#CUDA_VISIBLE_DEVICES=0,1,2,3 python single_channel_multi_task_cls.py --root ../data/zhizhen_new/LabelImages/512 --traincsv ../data/zhizhen_new/LabelImages/train_multi.csv --valcsv ../data/zhizhen_new/LabelImages/val_multi.csv --testcsv ../data/zhizhen_new/LabelImages/test_multi.csv --model dsn121 --batch 16 --workers 4 --epoch 150 --display 50 --crop 448 --size 512 --weigh /home/weidong/code/github/DiabeticRetinopathy_solution/paper_data/output/kaggle_multi_task_cls_train_20170912195752_dsn121_multi_task/kaggle_multi_task_cls_dr_dsn121_017_best.pth

#CUDA_VISIBLE_DEVICES=0,1,2,3 python single_channel_multi_task_cls.py --root ../data/zhizhen_new/LabelImages/512 --traincsv ../data/zhizhen_new/LabelImages/train_multi.csv --valcsv ../data/zhizhen_new/LabelImages/val_multi.csv --testcsv ../data/zhizhen_new/LabelImages/val_multi.csv --model dsn121 --batch 16 --workers 4 --epoch 150 --display 50 --crop 448 --size 512 --weigh /home/weidong/code/github/DiabeticRetinopathy_solution/paper_data/output/kaggle_multi_task_cls_train_20170912195752_dsn121_multi_task/kaggle_multi_task_cls_dr_dsn121_017_best.pth --phase test

#CUDA_VISIBLE_DEVICES=0,1,2,3 python single_channel_multi_task_cls.py --root ../data/zhizhen_new/LabelImages/512 --traincsv ../data/zhizhen_new/LabelImages/train_multi.csv --valcsv ../data/zhizhen_new/LabelImages/val_multi.csv --testcsv ../data/zhizhen_new/LabelImages/test_multi.csv --model rsn34 --batch 64 --workers 4 --epoch 150 --display 50 --crop 448 --size 512









CUDA_VISIBLE_DEVICES=0,1,2,3 python single_channel_multi_task_cls_2.py --root ../data/zhizhen_new/LabelImages/512 --traincsv ../data/zhizhen_new/LabelImages/train_multi.csv --valcsv ../data/zhizhen_new/LabelImages/val_multi.csv --testcsv ../data/zhizhen_new/LabelImages/test_multi.csv --model rsn34 --batch 64 --workers 4 --epoch 150 --display 50 --crop 448 --size 512 --weight /home/weidong/code/github/DiabeticRetinopathy_solution/paper_data/output/kaggle_multi_task_cls_train_20170913192757_rsn34_multi_task/kaggle_multi_task_cls_dr_rsn34_015_best.pth --phase test



#CUDA_VISIBLE_DEVICES=0,1,2,3 python single_channel_multi_task_cls_2.py --root ../data/zhizhen_new/LabelImages/512 --traincsv ../data/zhizhen_new/LabelImages/train_multi.csv --valcsv ../data/zhizhen_new/LabelImages/val_multi.csv --testcsv ../data/zhizhen_new/LabelImages/test_multi.csv --model rsn34 --batch 64 --workers 4 --epoch 150 --display 50 --crop 448 --size 512 --weight /home/weidong/code/github/DiabeticRetinopathy_solution/paper_data/output/kaggle_multi_task_cls_train_20170913192757_rsn34_multi_task/kaggle_multi_task_cls_dr_rsn34_002_best.pth --phase test