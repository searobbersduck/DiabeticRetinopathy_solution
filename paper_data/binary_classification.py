import json
import torch.utils.data
import numpy as np
from PIL import Image
import sys
sys.path.append('../')
from utils import TenCrop, HorizontalFlip, Affine, ColorJitter, Lighting, PILColorJitter
from utils import AverageMeter, quadratic_weighted_kappa
import torchvision.transforms as transforms
import pandas as pd

import argparse
import os

from torch.utils.data import DataLoader
import torchvision
import torch.nn as nn
import math

import torch.nn.functional as F
import torch.optim as optim
from torch.autograd import Variable

import torch.backends.cudnn as cudnn

import time


def parse_args():
    parser = argparse.ArgumentParser(description='binary classification')

    parser.add_argument('--root', required=True)
    parser.add_argument('--traincsv', default=None)
    parser.add_argument('--valcsv', default=None)
    parser.add_argument('--testcsv', default=None)

    parser.add_argument('--exp', required=True, help='The name of experiment')
    parser.add_argument('--dataset', default='kaggle', choices=['kaggle'], help='The dataset to use')
    parser.add_argument('--phase', default='train')
    parser.add_argument('--model', default='googlenet', choices=['googlenet'])
    parser.add_argument('--batch', default=8, type=int, help='The batch size of training')
    parser.add_argument('--crop', default=448, type=int, help='The crop size of input')
    parser.add_argument('--size', default=512, type=int, choices=[128,256,512,1024], help='The scale size of input')
    parser.add_argument('--weight', default=None, help='The path of pretrained model')
    parser.add_argument('--lr', default=0.01, type=float)
    parser.add_argument('--mom', default=0.9, type=float)
    parser.add_argument('--wd', default=1e-4, type=float)
    parser.add_argument('--fix', default=100, type=int)
    parser.add_argument('--step', default=100, type=int)
    parser.add_argument('--epoch', default=300, type=int)
    parser.add_argument('--display', default=10, type=int, help='The frequency of print log')
    parser.add_argument('--seed', default=111, type=int)
    parser.add_argument('--workers', default=4, type=int)
    parser.add_argument('--baseline', action='store_true')
    parser.add_argument('--output', default='output', help='The output dir')

    return parser.parse_args()

opt = parse_args()

print(opt)

class BinClsDataSet(torch.utils.data.Dataset):
    def __init__(self, root, config, crop_size, scale_size, baseline=False):
        super(BinClsDataSet, self).__init__()
        self.root = root
        self.config = config
        self.crop_size = crop_size
        self.scale_size = scale_size
        df = pd.DataFrame.from_csv(config)
        self.images_list = []
        for index, row in df.iterrows():
            self.images_list.append(row)
        with open('info.json', 'r') as fp:
            info = json.load(fp)
        mean_values = torch.from_numpy(np.array(info['mean'], dtype=np.float32) / 255)
        std_values = torch.from_numpy(np.array(info['std'], dtype=np.float32) / 255)
        eigen_values = torch.from_numpy(np.array(info['eigval'], dtype=np.float32))
        eigen_vectors = torch.from_numpy(np.array(info['eigvec'], dtype=np.float32))
        if baseline:
            self.transform = transforms.Compose([
                transforms.RandomCrop(crop_size),
                transforms.Scale(299),
                transforms.RandomHorizontalFlip(),
                transforms.ToTensor(),
                transforms.Normalize(mean=mean_values, std=std_values),
            ])
        else:
            self.transform = transforms.Compose([
                transforms.RandomCrop(crop_size),
                transforms.Scale(299),
                transforms.RandomHorizontalFlip(),
                PILColorJitter(),
                transforms.ToTensor(),
                Lighting(alphastd=0.01, eigval=eigen_values, eigvec=eigen_values),
                transforms.Normalize(mean=mean_values, std=std_values),
            ])

    def __getitem__(self, item):
        return self.transform(Image.open(os.path.join(self.root, self.images_list[item][0]+'_'+str(self.scale_size)+'.png'))), self.images_list[item][2]

    def __len__(self):
        return len(self.images_list)

class BinClsDataSetVal(torch.utils.data.Dataset):
    def __init__(self, root, config, crop_size, scale_size, baseline=False):
        super(BinClsDataSetVal, self).__init__()
        self.root = root
        self.config = config
        self.crop_size = crop_size
        self.scale_size = scale_size
        df = pd.DataFrame.from_csv(config)
        self.images_list = []
        for index, row in df.iterrows():
            self.images_list.append(row)
        with open('info.json', 'r') as fp:
            info = json.load(fp)
        mean_values = torch.from_numpy(np.array(info['mean'], dtype=np.float32) / 255)
        std_values = torch.from_numpy(np.array(info['std'], dtype=np.float32) / 255)
        eigen_values = torch.from_numpy(np.array(info['eigval'], dtype=np.float32))
        eigen_vectors = torch.from_numpy(np.array(info['eigvec'], dtype=np.float32))
        self.transform = transforms.Compose([
            transforms.CenterCrop(crop_size),
            transforms.Scale(299),
            transforms.ToTensor(),
            transforms.Normalize(mean=mean_values, std=std_values),
        ])

    def __getitem__(self, item):
        return self.transform(Image.open(os.path.join(self.root, self.images_list[item][0]+'_'+str(self.scale_size)+'.png'))), self.images_list[item][2]

    def __len__(self):
        return len(self.images_list)

def test_dataset():
    dataset = DataLoader(BinClsDataSet(opt.root, opt.labelscsv, 224, 512), batch_size=16)
    for index, (images, labels) in enumerate(dataset):
        torchvision.utils.save_image(images, './test.jpeg')
        print(labels)

def initial_cls_weights(cls):
    for m in cls.modules():
        if isinstance(m, nn.Conv2d):
            n = m.kernel_size[0]*m.kernel_size[1]*m.out_channels
            m.weight.data.normal_(0, math.sqrt(2./n))
            if m.bias is not None:
                m.bias.data.zero_()
        if isinstance(m, nn.BatchNorm2d):
            m.weight.data.fill_(1)
            m.bias.data.zero_()
        if isinstance(m, nn.Linear):
            m.weight.data.normal_(0, 0.01)
            m.bias.data.zero_()


class TestCls(nn.Module):
    def __init__(self, model, weights=None):
        super(TestCls, self).__init__()
        self.model = model

        self.base_model = nn.Sequential(
            *list(model.children())[0:3],
            nn.MaxPool2d(3,2),
            *list(model.children())[3:5],
            nn.MaxPool2d(3, 2),
            *list(model.children())[5:13],
            *list(model.children())[14:-1],
            nn.AvgPool2d(kernel_size=8),
            nn.Dropout(),
        )

        self.base_model0 = nn.Sequential(*list(model.children())[0:3])
        self.base_model1 = nn.Sequential(*list(model.children())[3:5])
        self.base_model2 = nn.Sequential(*list(model.children())[5:13])
        self.base_model3 = nn.Sequential(*list(model.children())[14:-1])

        self.aux = list(model.children())[13]
        self.fc = nn.Linear(2048, 2)
        self.cls = nn.Sequential(nn.Conv2d(2048, 5, kernel_size=1, stride=1, padding=0, bias=True))
        initial_cls_weights(self.cls)
        if weights:
            self.load_state_dict(torch.load(weights))
    def forward(self, x):
        x = self.base_model0(x)
        x = F.max_pool2d(x, kernel_size=3, stride=2)
        x = self.base_model1(x)
        x = F.max_pool2d(x, kernel_size=3, stride=2)
        x = self.base_model2(x)
        x = self.base_model3(x)
        x = F.avg_pool2d(x, kernel_size=8)
        x = F.dropout(x, training=self.training)
        x = x.view(x.size(0), -1)
        x = self.fc(x)
        return x


def cls_train(train_data_loader, model, criterion, optimizer, epoch, display):
    model.train()
    tot_pred = np.array([], dtype=int)
    tot_label = np.array([], dtype=int)
    batch_time = AverageMeter()
    data_time = AverageMeter()
    losses = AverageMeter()
    accuracy = AverageMeter()
    end = time.time()
    logger = []
    for num_iter, (images, labels) in enumerate(train_data_loader):
        data_time.update(time.time()-end)
        output = model(Variable(images.cuda()))
        loss = criterion(output, Variable(labels.cuda()))
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        batch_time.update(time.time()-end)
        _,pred = torch.max(output, 1)
        pred = pred.cpu().data.numpy().squeeze()
        labels = labels.numpy().squeeze()
        tot_pred = np.append(tot_pred, pred)
        tot_label = np.append(tot_label, labels)
        losses.update(loss.data[0], len(images))
        accuracy.update(np.equal(pred, labels).sum()/len(labels), len(labels))
        end = time.time()
        if num_iter % display == 0:
            correct = np.equal(tot_pred, tot_label).sum()/len(tot_pred)
            print_info = 'Epoch: [{0}][{1}/{2}]\tTime {batch_time.val:3f} ({batch_time.avg:.3f})\t'\
                'Data {data_time.avg:.3f}\t''Loss {loss.avg:.4f}\tAccuray {accuracy.avg:.4f}'.format(
                epoch, num_iter, len(train_data_loader),batch_time=batch_time, data_time=data_time,
                loss=losses, accuracy=accuracy
            )
            print(print_info)
            logger.append(print_info)
    return logger

def cls_eval(eval_data_loader, model, criterion, display):
    model.eval()
    tot_pred = np.array([], dtype=int)
    tot_label = np.array([], dtype=int)
    batch_time = AverageMeter()
    data_time = AverageMeter()
    losses = AverageMeter()
    accuracy = AverageMeter()
    end = time.time()
    logger = []
    for num_iter, (image, label) in enumerate(eval_data_loader):
        data_time.update(time.time()-end)
        output = model(Variable(image.cuda()))
        loss = criterion(output, Variable(label.cuda()))
        _,pred = torch.max(output, 1)
        pred = pred.cpu().data.numpy().squeeze()
        label = label.numpy().squeeze()
        losses.update(loss.data[0], len(image))
        batch_time.update(time.time()-end)
        accuracy.update(np.equal(pred, label).sum()/len(label), len(label))
        end = time.time()
        print_info = 'Eval: [{0}/{1}]\tTime {batch_time.val:3f} ({batch_time.avg:.3f})\t' \
                     'Data {data_time.avg:.3f}\t''Loss {loss.avg:.4f}\tAccuray {accuracy.avg:.4f}'.format(
            num_iter, len(eval_data_loader), batch_time=batch_time, data_time=data_time,
            loss=losses, accuracy=accuracy
        )
        logger.append(print_info)
        print(print_info)
    return accuracy.avg, logger

def main():
    print('===> Parsing options')
    opt = parse_args()
    print(opt)
    cudnn.benchmark = True
    torch.manual_seed(opt.seed)
    if not torch.cuda.is_available():
        raise Exception('No GPU found!')
    if not os.path.isdir(opt.output):
        os.makedirs(opt.output)
    time_stamp = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
    output_dir = os.path.join(opt.output, opt.dataset+'_cls_'+opt.phase+'_'+time_stamp+'_'+opt.model+'_'+opt.exp)
    if not os.path.exists(output_dir):
        print('====> Creating ', output_dir)
        os.makedirs(output_dir)

    print('====> Building model:')

    model = torchvision.models.inception_v3(True)
    model = TestCls(model, opt.weight)
    model_cuda = nn.DataParallel(model).cuda()
    criterion = nn.CrossEntropyLoss().cuda()

    if opt.phase == 'train':
        print('====> Training model')
        dataset_train = DataLoader(BinClsDataSet(opt.root, opt.traincsv, opt.crop, opt.size), batch_size=opt.batch, num_workers=opt.workers,
                             shuffle=True, pin_memory=True)
        dataset_val = DataLoader(BinClsDataSetVal(opt.root, opt.valcsv, opt.crop, opt.size), batch_size=opt.batch,
                             num_workers=opt.workers,
                             shuffle=False, pin_memory=False)
        accuracy_best = 0
        for epoch in range(opt.epoch):
            if epoch < opt.fix:
                lr = opt.lr
            else:
                lr = opt.lr * (0.1 ** (epoch // opt.step))
            optimizer = optim.SGD(
                [{'params': model.base_model0.parameters()}, {'params': model.base_model1.parameters()},
                 {'params': model.base_model2.parameters()},
                 {'params': model.base_model3.parameters()},
                 {'params': model.fc.parameters()}],
                lr=lr,
                momentum=opt.mom,
                weight_decay=opt.wd,
                nesterov=True)
            logger = cls_train(dataset_train, nn.DataParallel(model).cuda(), criterion, optimizer, epoch, opt.display)

            acc, logger_val = cls_eval(dataset_val, nn.DataParallel(model).cuda(), criterion, opt.display)

            if acc > accuracy_best:
                print('\ncurrent best accuracy is: {}\n'.format(acc))
                accuracy_best = acc
                torch.save(model.cpu().state_dict(), os.path.join(output_dir, opt.dataset+'_binarycls_'+opt.model+'_%03d'%epoch+'_best.pth'))
                print('====> Save model: {}'.format(os.path.join(output_dir, opt.dataset+'_binarycls_'+opt.model+'_%03d'%epoch+'_best.pth')))
            if not os.path.isfile(os.path.join(output_dir, 'train.log')):
                with open(os.path.join(output_dir, 'train.log'), 'w') as fp:
                    fp.write(str(opt)+'\n\n')
            with open(os.path.join(output_dir, 'train.log'), 'a') as fp:
                fp.write('\n' + '\n'.join(logger))
                fp.write('\n' + '\n'.join(logger_val))
    elif opt.phase == 'test':
        if opt.weight:
            print('====> Evaluating model')
            dataset_test = DataLoader(BinClsDataSetVal(opt.root, opt.testcsv, opt.size, opt.size), batch_size=opt.batch,
                                      num_workers=opt.workers,
                                      shuffle=False, pin_memory=False)
            acc, logger_test = cls_eval(dataset_test, nn.DataParallel(model).cuda(), criterion, opt.display)
            with open(os.path.join(output_dir, 'test.log'), 'w') as fp:
                fp.write(str(opt) + '\n')
                fp.write('\n====> Accuracy: %.4f' % acc)
            print('\n====> Accuracy: %.4f' % acc)
        else:
            raise Exception('No weights found!')
    else:
        raise Exception('No phase found')

if __name__ == '__main__':
    main()

