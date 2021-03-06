import os
import numpy as np
from PIL import Image, ImageFilter
from image_squeene import compress_image, get_size, MyGaussianBlur
import random
from sklearn.model_selection import train_test_split
from PIL import ImageFile
import traceback
import cv2
import sys
from gen_8_map import gen_8_2_map as gen_8_map
import matplotlib.pyplot as plt
ImageFile.LOAD_TRUNCATED_IMAGES = True


class DataParser():
    def __init__(self, batch_size_train):
        #
        self.train_file = '/media/liu/File/debug_data/tamper_result'
        self.double_edge_file = '/media/liu/File/debug_data/ground_truth_result'
        #
        # self.train_file = '/media/liu/File/8_20_dataset_after_divide/train_dataset_train_percent_0.80@8_20'
        # self.double_edge_file = '/media/liu/File/8_20_dataset_after_divide/train_gt_train_percent_0.80@8_20'

        # after resize splicing data
        # self.train_file = '/media/liu/File/Sp_320_dataset/tamper_result_320'
        # self.double_edge_file = '/media/liu/File/Sp_320_dataset/ground_truth_result_320'
        # sp_data_flag = True




        self.train_list = os.listdir(self.train_file)
        # self.double_edge_list = os.listdir(self.double_edge_file)
        self.double_edge_list =[]
        for item in self.train_list:
            temp = item.replace('poisson', 'Gt')
            temp = temp.replace('Default','Gt')
            temp = temp.replace('png','bmp')
            temp = temp.replace('jpg', 'bmp')
            self.double_edge_list.append(temp)

        for item in self.train_list:
            temp = item.replace('poisson', 'Gt')
            temp = temp.replace('Default','Gt')
            temp = temp.replace('png','bmp')
            temp = temp.replace('jpg', 'bmp')
            self.double_edge_list.append(temp)


        self.ground_list = []
        self.trainimage_list = []
        self.batch_size = batch_size_train
        self.gt_list = []
        self.train_image_list = []
        self.dou_edge_list = []
        self.final_dou_edge_list = []



        for i in range(len(self.train_list)):
            train_filename = os.path.join(self.train_file, self.train_list[i])
            gt_filename = os.path.join(self.double_edge_file,self.double_edge_list[i])

            t1 = self.train_list[i]
            t1 = t1.replace('poisson','')
            t1 = t1.replace('Default', '')
            t1 = t1.replace('png','')
            t1 = t1.replace('jpg','')
            t1 = t1.replace('bmp','')

            t2 = self.double_edge_list[i]
            t2 = t2.replace('Gt', '')
            t2 = t2.replace('png', '')
            t2 = t2.replace('jpg', '')
            t2 = t2.replace('bmp', '')
            if t1!=t2:
                print(t1)
                print(t2)
                print('数据和GT不匹配')
                traceback.print_exc()

            self.train_image_list.append(train_filename)
            self.gt_list.append(gt_filename)
        self.X_train, self.X_test, self.Y_train, self.Y_test = train_test_split(self.train_image_list, self.gt_list, test_size=0.1, train_size=0.9,random_state=1300)


        self.steps_per_epoch = len(self.X_train) / batch_size_train
        self.val_steps = len(self.X_test) / (batch_size_train)

        self.image_width = 320
        self.image_height = 320

        self.target_regression = True

    def get_batch(self, batch, train=True):

        filenames = []
        images = []
        edgemaps = []
        double_edge = []
        edgemaps_4 = []
        edgemaps_8 = []
        edgemaps_16 = []
        chanel1 = []
        chanel2 = []
        chanel3 = []
        chanel4 = []
        chanel5 = []
        chanel6 = []
        chanel7 = []
        chanel8 = []
        chanelfuse = []
        chanel = [[] for i in range(8)]        

        for idx, b in enumerate(batch):
            if train:
                index = self.X_train.index(b)
                im = Image.open(self.X_train[index])
                dou_path = os.path.join(self.double_edge_file, self.Y_train[index].split('/')[-1])
                dou_em = Image.open(dou_path)
                # 在这里获取8张图，从左上角按照顺时针顺序,返回的是一个长度为8的列表
                relation_8_map = gen_8_map(dou_em)
                for i in range(8):
                    relation_8_map[i] = Image.fromarray(relation_8_map[i].astype('uint8')).convert('RGB')


                weight = im.size[0]
                height = im.size[1]
                if im.size[0] > 320 and im.size[1] > 320:
                    w_centry = weight // 2
                    h_centry = height // 2

                    if w_centry > 160:
                        range_w = random.randint(0, w_centry - 160)
                    else:
                        range_w = 0
                    if h_centry > 160:
                        range_h = random.randint(0, h_centry - 160)
                    else:
                        range_h = 0

                    # 决定图像是否加压缩
                    if random.randint(0, 20) == 1:

                        try:
                            mb = random.randint(30, 100)
                            path = compress_image(infile=self.X_train[index], mb=mb)
                            im = Image.open(path)
                        except:
                            traceback.print_exc()
                    # 决定图像是否加模糊
                    if random.randint(0, 20) == 1:
                        m = random.randint(0, 5)
                        if m == 0:
                            r = random.randint(1, 3)
                            im = im.filter(ImageFilter.GaussianBlur(radius=r))
                        else:
                            pass

                    if random.randint(0, 1) == 0:
                        im = im.crop((w_centry - 160 + range_w, h_centry - 160 + range_h, w_centry + 160 + range_w,
                                      h_centry + 160 + range_h))
                        dou_em = dou_em.crop(
                            (w_centry - 160 + range_w, h_centry - 160 + range_h, w_centry + 160 + range_w,
                             h_centry + 160 + range_h))
                        for i in range(8):
                            relation_8_map[i] = relation_8_map[i].crop(
                                (w_centry - 160 + range_w, h_centry - 160 + range_h, w_centry + 160 + range_w,
                                 h_centry + 160 + range_h))


                    else:
                        im = im.crop((w_centry - 160 - range_w, h_centry - 160 - range_h, w_centry + 160 - range_w,
                                      h_centry + 160 - range_h))

                        dou_em = dou_em.crop(
                            (w_centry - 160 - range_w, h_centry - 160 - range_h, w_centry + 160 - range_w,
                             h_centry + 160 - range_h))
                        for i in range(8):
                            relation_8_map[i] = relation_8_map[i].crop(
                                (w_centry - 160 - range_w, h_centry - 160 - range_h, w_centry + 160 - range_w,
                                 h_centry + 160 - range_h))

                        # 决定是否flip 旋转
                        random_aug = random.randint(0, 20)
                        try:
                            if random_aug < 5:
                                if random_aug == 0:
                                    # 旋转90
                                    im = im.transpose(Image.ROTATE_90)
                                    dou_em = dou_em.transpose(Image.ROTATE_90)
                                    for i in range(8):
                                        relation_8_map[i] = relation_8_map[i].transpose(Image.ROTATE_90)

                                elif random_aug == 1:
                                    # 旋转180
                                    im = im.transpose(Image.ROTATE_180)
                                    dou_em = dou_em.transpose(Image.ROTATE_180)
                                    for i in range(8):
                                        relation_8_map[i] = relation_8_map[i].transpose(Image.ROTATE_180)

                                elif random_aug == 2:
                                    # 旋转270
                                    im = im.transpose(Image.ROTATE_270)
                                    dou_em = dou_em.transpose(Image.ROTATE_270)
                                    for i in range(8):
                                        relation_8_map[i] = relation_8_map[i].transpose(Image.ROTATE_270)
                                elif random_aug == 3:
                                    # 左右呼唤
                                    im = im.transpose(Image.FLIP_LEFT_RIGHT)
                                    dou_em = dou_em.transpose(Image.FLIP_LEFT_RIGHT)
                                    for i in range(8):
                                        relation_8_map[i] = relation_8_map[i].transpose(Image.FLIP_LEFT_RIGHT)
                                elif random_aug == 4:
                                    # 左右呼唤
                                    im = im.transpose(Image.FLIP_TOP_BOTTOM)
                                    dou_em = dou_em.transpose(Image.FLIP_TOP_BOTTOM)
                                    for i in range(8):
                                        relation_8_map[i] = relation_8_map[i].transpose(Image.FLIP_TOP_BOTTOM)
                        except:
                            traceback.print_exc()
                else:
                    # 决定图像是否加压缩
                    if random.randint(0, 20) == 1:
                        # o_size = get_size(self.X_train[index])
                        try:
                            mb = random.randint(30, 100)
                            path = compress_image(infile=self.X_train[index], mb=mb)
                            im = Image.open(path)
                        except:
                            traceback.print_exc()
                    # 决定图像是否加模糊
                    if random.randint(0, 20) == 1:
                        m = random.randint(0, 5)
                        if m == 0:
                            r = random.randint(1, 3)
                            im = im.filter(ImageFilter.GaussianBlur(radius=r))
                        else:
                            pass
                            # x = random.randint(0, 200)
                            # y = random.randint(0, 200)
                            # bounds_x = random.randint(20, 100)
                            # bounds_y = random.randint(20, 100)
                            # bounds = (x, y, x + bounds_x, y + bounds_y)
                            # r = random.randint(1, 3)
                            # im = im.filter(MyGaussianBlur(radius=r, bounds=bounds))

                    im = im.crop((0, 0, self.image_height, self.image_width))

                    dou_em = dou_em.crop((0, 0, self.image_height, self.image_width))
                    for i in range(8):
                        relation_8_map[i] = relation_8_map[i].crop((0, 0, self.image_height, self.image_width))


                    # chanel_1_1 = chanel_1_1.crop((0, 0, self.image_height, self.image_width))
                    # chanel_10 = chanel_10.crop((0, 0, self.image_height, self.image_width))
                    # chanel_11 = chanel_11.crop((0, 0, self.image_height, self.image_width))
                    # chanel0_1 = chanel0_1.crop((0, 0, self.image_height, self.image_width))
                    # chanel01 = chanel01.crop((0, 0, self.image_height, self.image_width))
                    # chanel1_1 = chanel1_1.crop((0, 0, self.image_height, self.image_width))
                    # chanel10 = chanel10.crop((0, 0, self.image_height, self.image_width))
                    # chanel11 = chanel11.crop((0, 0, self.image_height, self.image_width))

                # print(im)
                im = np.array(im, dtype=np.float32)
                im = im[..., ::-1]  # RGB 2 BGR
                # R = im[..., 0].mean()
                # G = im[..., 1].mean()
                # B = im[..., 2].mean()
                # im[..., 0] -= R
                # im[..., 1] -= G
                # im[..., 2] -= B

                # R=118.98194217348079 G=127.4061956623793 B=138.00865419127499
                im[..., 0] -= 138.008
                im[..., 1] -= 127.406
                im[..., 2] -= 118.982

                dou_chanel = [0 for i in range(8)]

                for i in range(8):
                    dou_chanel[i] = np.array(relation_8_map[i], dtype=np.float32)
                    dou_chanel[i] = np.array(dou_chanel[i][:, :, 1:])
                    # dou_chanel[i] = dou_chanel[i] / 255
                    chanel[i].append(dou_chanel[i])

                c_1 = dou_chanel[0][:, :, 1:]
                c_2 = dou_chanel[1][:, :, 1:]
                c_3 = dou_chanel[2][:, :, 1:]
                c_4 = dou_chanel[3][:, :, 1:]
                c_5 = dou_chanel[4][:, :, 1:]
                c_6 = dou_chanel[5][:, :, 1:]
                c_7 = dou_chanel[6][:, :, 1:]
                c_8 = dou_chanel[7][:, :, 1:]
                final_c = np.concatenate((c_1, c_2, c_3, c_4, c_5, c_6, c_7, c_8), axis=2)
                chanelfuse.append(final_c)
                #
                # dou_em = np.array(dou_em, dtype=np.float32)
                # dou_em = np.array(dou_em[:, :, :])
                # dou_em = np.expand_dims(dou_em, 2)
                # double_edge.append(dou_em)


                dou_em = np.array(dou_em, dtype=np.float32)
                # 转化为无类别的GT 100 255 为边缘
                dou_em = np.where(dou_em == 50,0,dou_em)
                dou_em = np.where(dou_em ==100,1,dou_em)
                dou_em = np.where(dou_em == 255,1,dou_em)
                dou_em = np.array(dou_em[:, :])
                dou_em = np.expand_dims(dou_em, 2)

                double_edge.append(dou_em)
                t_4 = dou_em.squeeze(2)
                t_4 = Image.fromarray(t_4)
                t_4 = t_4.resize((40,40),Image.BICUBIC)
                t_4 = np.where(np.array(t_4)>0,1,0)
                # plt.figure('40')
                # plt.imshow(t_4)
                # plt.show()
                t_4 = np.expand_dims(t_4,2)
                edgemaps_4.append(t_4)

                t_8 = dou_em.squeeze(2)
                t_8 = Image.fromarray(t_8)
                t_8 = t_8.resize((80, 80), Image.BICUBIC)
                t_8 = np.where(np.array(t_8) > 0, 1, 0)
                # plt.figure('80')
                # plt.imshow(t_8)
                # plt.show()
                t_8 = np.expand_dims(t_8, 2)
                edgemaps_8.append(t_8)

                t_16 = dou_em.squeeze(2)
                t_16 = Image.fromarray(t_16)
                t_16 = t_16.resize((160, 160), Image.BICUBIC)
                t_16 = np.where(np.array(t_16) > 0, 1, 0)
                # plt.figure('160')
                # plt.imshow(t_16)
                # plt.show()
                t_16 = np.expand_dims(t_16, 2)
                edgemaps_16.append(t_16)


                images.append(im)
                # edgemaps.append(bin_em)
                # edgemaps_4.append(bin_em4)
                # edgemaps_8.append(bin_em8)
                # edgemaps_16.append(bin_em16)
                filenames.append(self.X_train[index])

            else:
                index = self.X_test.index(b)
                im = Image.open(self.X_test[index])
                #
                # index = self.X_train.index(b)
                # im = Image.open(self.X_train[index])
                dou_path = os.path.join(self.double_edge_file, self.Y_test[index].split('/')[-1])
                dou_em = Image.open(dou_path)

                # 在这里获取8张图，从左上角按照顺时针顺序,返回的是一个长度为8的列表
                relation_8_map = gen_8_map(dou_em)
                for i in range(8):
                    relation_8_map[i] = Image.fromarray(relation_8_map[i].astype('uint8')).convert('RGB')

                weight = im.size[0]
                height = im.size[1]
                if im.size[0] > 320 and im.size[1] > 320:
                    w_centry = weight // 2
                    h_centry = height // 2

                    if w_centry > 160:
                        range_w = random.randint(0, w_centry - 160)
                    else:
                        range_w = 0
                    if h_centry > 160:
                        range_h = random.randint(0, h_centry - 160)
                    else:
                        range_h = 0

                    # 决定图像是否加压缩
                    if random.randint(0, 20) == 1:

                        try:
                            mb = random.randint(30, 100)
                            path = compress_image(infile=self.X_test[index], mb=mb)
                            im = Image.open(path)
                        except:
                            traceback.print_exc()
                    # 决定图像是否加模糊
                    if random.randint(0, 20) == 1:
                        m = random.randint(0, 5)
                        if m == 0:
                            r = random.randint(1, 3)
                            im = im.filter(ImageFilter.GaussianBlur(radius=r))
                        else:
                            pass

                    if random.randint(0, 1) == 0:
                        im = im.crop((w_centry - 160 + range_w, h_centry - 160 + range_h, w_centry + 160 + range_w,
                                      h_centry + 160 + range_h))
                        dou_em = dou_em.crop(
                            (w_centry - 160 + range_w, h_centry - 160 + range_h, w_centry + 160 + range_w,
                             h_centry + 160 + range_h))
                        for i in range(8):
                            relation_8_map[i] = relation_8_map[i].crop(
                                (w_centry - 160 + range_w, h_centry - 160 + range_h, w_centry + 160 + range_w,
                                 h_centry + 160 + range_h))


                    else:
                        im = im.crop((w_centry - 160 - range_w, h_centry - 160 - range_h, w_centry + 160 - range_w,
                                      h_centry + 160 - range_h))

                        dou_em = dou_em.crop(
                            (w_centry - 160 - range_w, h_centry - 160 - range_h, w_centry + 160 - range_w,
                             h_centry + 160 - range_h))
                        for i in range(8):
                            relation_8_map[i] = relation_8_map[i].crop(
                                (w_centry - 160 - range_w, h_centry - 160 - range_h, w_centry + 160 - range_w,
                                 h_centry + 160 - range_h))

                        # 决定是否flip 旋转
                        random_aug = random.randint(0, 20)
                        try:
                            if random_aug < 5:
                                if random_aug == 0:
                                    # 旋转90
                                    im = im.transpose(Image.ROTATE_90)
                                    dou_em = dou_em.transpose(Image.ROTATE_90)
                                    for i in range(8):
                                        relation_8_map[i] = relation_8_map[i].transpose(Image.ROTATE_90)

                                elif random_aug == 1:
                                    # 旋转180
                                    im = im.transpose(Image.ROTATE_180)
                                    dou_em = dou_em.transpose(Image.ROTATE_180)
                                    for i in range(8):
                                        relation_8_map[i] = relation_8_map[i].transpose(Image.ROTATE_180)

                                elif random_aug == 2:
                                    # 旋转270
                                    im = im.transpose(Image.ROTATE_270)
                                    dou_em = dou_em.transpose(Image.ROTATE_270)
                                    for i in range(8):
                                        relation_8_map[i] = relation_8_map[i].transpose(Image.ROTATE_270)
                                elif random_aug == 3:
                                    # 左右呼唤
                                    im = im.transpose(Image.FLIP_LEFT_RIGHT)
                                    dou_em = dou_em.transpose(Image.FLIP_LEFT_RIGHT)
                                    for i in range(8):
                                        relation_8_map[i] = relation_8_map[i].transpose(Image.FLIP_LEFT_RIGHT)
                                elif random_aug == 4:
                                    # 左右呼唤
                                    im = im.transpose(Image.FLIP_TOP_BOTTOM)
                                    dou_em = dou_em.transpose(Image.FLIP_TOP_BOTTOM)
                                    for i in range(8):
                                        relation_8_map[i] = relation_8_map[i].transpose(Image.FLIP_TOP_BOTTOM)
                        except:
                            traceback.print_exc()
                else:
                    # 决定图像是否加压缩
                    if random.randint(0, 20) == 1:
                        # o_size = get_size(self.X_train[index])
                        try:
                            mb = random.randint(30, 100)
                            path = compress_image(infile=self.X_test[index], mb=mb)
                            im = Image.open(path)
                        except:
                            traceback.print_exc()
                    # 决定图像是否加模糊
                    if random.randint(0, 20) == 1:
                        m = random.randint(0, 5)
                        if m == 0:
                            r = random.randint(1, 3)
                            im = im.filter(ImageFilter.GaussianBlur(radius=r))
                        else:
                            pass
                            # x = random.randint(0, 200)
                            # y = random.randint(0, 200)
                            # bounds_x = random.randint(20, 100)
                            # bounds_y = random.randint(20, 100)
                            # bounds = (x, y, x + bounds_x, y + bounds_y)
                            # r = random.randint(1, 3)
                            # im = im.filter(MyGaussianBlur(radius=r, bounds=bounds))

                    im = im.crop((0, 0, self.image_height, self.image_width))

                    dou_em = dou_em.crop((0, 0, self.image_height, self.image_width))
                    for i in range(8):
                        relation_8_map[i] = relation_8_map[i].crop((0, 0, self.image_height, self.image_width))


                # print(im)
                im = np.array(im, dtype=np.float32)
                im = im[..., ::-1]  # RGB 2 BGR


                # R=118.98194217348079 G=127.4061956623793 B=138.00865419127499
                im[..., 0] -= 138.008
                im[..., 1] -= 127.406
                im[..., 2] -= 118.982

                dou_chanel = [0 for i in range(8)]

                for i in range(8):
                    dou_chanel[i] = np.array(relation_8_map[i], dtype=np.float32)
                    dou_chanel[i] = np.array(dou_chanel[i][:, :, 1:])
                    # dou_chanel[i] = dou_chanel[i] / 255
                    chanel[i].append(dou_chanel[i])

                c_1 = dou_chanel[0][:, :, 1:]
                c_2 = dou_chanel[1][:, :, 1:]
                c_3 = dou_chanel[2][:, :, 1:]
                c_4 = dou_chanel[3][:, :, 1:]
                c_5 = dou_chanel[4][:, :, 1:]
                c_6 = dou_chanel[5][:, :, 1:]
                c_7 = dou_chanel[6][:, :, 1:]
                c_8 = dou_chanel[7][:, :, 1:]
                final_c = np.concatenate((c_1, c_2, c_3, c_4, c_5, c_6, c_7, c_8), axis=2)
                chanelfuse.append(final_c)
                #
                # dou_em = np.array(dou_em, dtype=np.float32)
                # dou_em = np.array(dou_em[:, :, :])
                # dou_em = np.expand_dims(dou_em, 2)
                # double_edge.append(dou_em)

                dou_em = np.array(dou_em, dtype=np.float32)
                # 转化为无类别的GT 100 255 为边缘
                dou_em = np.where(dou_em == 50, 0, dou_em)
                dou_em = np.where(dou_em == 100, 1, dou_em)
                dou_em = np.where(dou_em == 255, 1, dou_em)
                dou_em = np.array(dou_em[:, :])
                dou_em = np.expand_dims(dou_em, 2)

                double_edge.append(dou_em)
                t_4 = dou_em.squeeze(2)
                t_4 = Image.fromarray(t_4)
                t_4 = t_4.resize((40,40),Image.BICUBIC)
                t_4 = np.where(np.array(t_4)>0,1,0)
                # plt.figure('40')
                # plt.imshow(t_4)
                # plt.show()
                t_4 = np.expand_dims(t_4,2)
                edgemaps_4.append(t_4)

                t_8 = dou_em.squeeze(2)
                t_8 = Image.fromarray(t_8)
                t_8 = t_8.resize((80, 80), Image.BICUBIC)
                # t_8 = np.where(np.array(t_8) > 0, 1, 0)
                # plt.figure('80')
                # plt.imshow(t_8)
                # plt.show()
                t_8 = np.expand_dims(t_8, 2)
                edgemaps_8.append(t_8)

                t_16 = dou_em.squeeze(2)
                t_16 = Image.fromarray(t_16)
                t_16 = t_16.resize((160, 160), Image.BICUBIC)
                t_16 = np.where(np.array(t_16) > 0, 1, 0)
                # plt.figure('160')
                # plt.imshow(t_16)
                # plt.show()
                t_16 = np.expand_dims(t_16, 2)
                edgemaps_16.append(t_16)



                images.append(im)


        images = np.asarray(images)
        # edgemaps = np.asarray(edgemaps)
        # edgemaps_4 = np.asanyarray(edgemaps_4)
        # edgemaps_8 = np.asanyarray(edgemaps_8)
        # edgemaps_16 = np.asanyarray(edgemaps_16)
        double_edge = np.asarray(double_edge)
        edgemaps_4 = np.asarray(edgemaps_4)
        edgemaps_8 = np.asarray(edgemaps_8)
        edgemaps_16 = np.asarray(edgemaps_16)

        chanel1 = np.asarray(chanel[0])
        chanel2 = np.asarray(chanel[1])
        chanel3 = np.asarray(chanel[2])
        chanel4 = np.asarray(chanel[3])
        chanel5 = np.asarray(chanel[4])
        chanel6 = np.asarray(chanel[5])
        chanel7 = np.asarray(chanel[6])
        chanel8 = np.asarray(chanel[7])
        chanelfuse = np.asarray(chanelfuse)
        # print('images size:',images.shape)
        # print('double_edge:', double_edge.shape)
        # print('chanel6',chanel1.shape)
        # print('fusion', chanelfuse.shape)

        return images, edgemaps, double_edge, chanel1, chanel2, chanel3, chanel4, chanel5, chanel6, chanel7, chanel8, chanelfuse, edgemaps_4, edgemaps_8, edgemaps_16, filenames


def generate_minibatches(dataParser, train=True):

    while True:
        if train:
            batch_ids = np.random.choice(dataParser.X_train, dataParser.batch_size)
            ims, ems, double_edge, chanel1, chanel2, chanel3, chanel4, chanel5, chanel6, chanel7, chanel8, chanel_fuse, edgemaps_4, edgemaps_8, edgemaps_16, _ = dataParser.get_batch(
                batch_ids)
        else:
            batch_ids = np.random.choice(dataParser.X_test, dataParser.batch_size)
            ims, ems, double_edge, chanel1, chanel2, chanel3, chanel4, chanel5, chanel6, chanel7, chanel8, chanel_fuse, edgemaps_4, edgemaps_8, edgemaps_16, _ = dataParser.get_batch(
                batch_ids, train=False)

        # datagen.flow()
        yield (ims, [chanel1, chanel2, chanel3, chanel4, chanel5, chanel6, chanel7, chanel8, ems, ems])



if __name__ == "__main__":
    # model
    dataParser = DataParser(2)
    batch_ids = np.random.choice(dataParser.X_train, dataParser.batch_size)
    dataParser.get_batch(batch_ids)
    try:
        generate_minibatches(dataParser=dataParser,train=True)
        print()
    except Exception as e:
        traceback.print_exc()