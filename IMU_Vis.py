# -*- coding: utf-8 -*- 
"""
Project: IMU_Path_Visualisation
Creator: Dengfenfen
Create time: 2020-01-10 10:51
IDE: PyCharm
Introduction: Class Vis is to read the input pos and euler files to generate path and gesture data and to generate the
              related path and gesture VTP files for paraview.
"""

import os
import numpy as np
import pandas as pd
import math
import vtk
from numba import jit

Re = 6378137                        # m
ECCENTRICITY = 0.0818191908426215   # Earth eccentricy, e2 = 2*f-f^2
E_SQR = ECCENTRICITY**2             # squared eccentricity
D2R = math.pi/180.0
threhold_angle = 5
    # 0.0873


class Vis(object):
    '''
    IMU path and gesture visualisation
    '''
    def __init__(self, data, header, trim_all_zero_row=True):
        '''
        Args:
            pos_file: pos_file should be a directory contains the position data files. Data files should be named as data_name.csv
                to define the GPS position. The .csv file should be organized as follows:
                  row 1: header line for columns [latitude, longitude,altitude], units[deg, deg, m]
                  the rest rows contain the specific position data
            eul_file: eul_file should be a directory contains the euler data files. Data files should be named as data_name.csv
                to define the euler angles . The .csv file should be organized as follows:
                 row 1: header line for columns [yaw, pitch,row], units[deg, deg, deg]
                  the rest rows contain the specific euler angles data
        '''
        self.pos_column = ['pos_lat (deg)', 'pos_lon (deg)', 'pos_alt (m)']
        self.euler_column = ['Yaw (deg)', 'Pitch (deg)', 'Roll (deg)']
        # 对于euler file 可以为空，但必须补全其相关header
        if len([i.strip() for i in header[3:]]) == 0:
            header[3:] = self.euler_column
        elif [i.strip() for i in header[3:]] != self.euler_column:
            raise ValueError("the euler header is not correct ")
        if len(data) == 0:
            raise ValueError("input file is empty")
        if trim_all_zero_row:
            # 删除LLA 和euler都为0的行
            index_path = np.where(data[:, 0:6] == 0)[0]
            data = np.delete(data, index_path, axis=0)
        self.pos_data = data[:, 0:3]
        self.euler_data = data[:, 3:6]
        self.pos_header = header[0:3]
        self.eul_header = header[3:6]
        # make sure input file is not empty
        if len(data) == 0:
            raise ValueError("input data is empty")
        # store the path data
        self.path_data = np.zeros(self.pos_data.shape)
        # store the gesture data, [ecef_postion_x, ecef_postion_y, ecef_postion_z,pos_xaxis_x, pos_xaxis_y, pos_xaxis_z,
        # pos_yaxis_x, pos_yaxis_y, pos_yaxis_z, pos_zaxis_x, pos_zaxis_y, pos_zaxis_z]
        self.gesture_data = np.zeros((self.euler_data.shape[0], 12))
        # store the unit vector coordinate of XYZ axis
        self.unit_vector_coord = np.zeros((self.euler_data.shape[0], 9))

        # store the quaternion of each row of euler angles
        self.quat = np.zeros((self.euler_data.shape[0], 4))
        # sore the accum quaternion
        self.Quat = np.zeros((self.euler_data.shape[0], 4))

    # @jit
    def gen_gesture_on_path(self, num):
        '''
        generate the position data and gesture data
        Args:
            num: 单位向量轴上的坐标点扩大的倍数
        '''
        #### read pos file from CSV and check its position data by checking the header
        self.__read_pos_from_csv()
        self.__gps_to_ecef()

        ### read euler file from CSV and check its euler data by checking the header
        self.__read_euler_from_csv()
        self.__euler_to_gesture()
        self.__gesture_for_path(num)

    def gen_vtk_for_path_gesture(self, what_vtk, vtk_path):
        '''
        generate VTP file for path or gesture in paraview
         Args:
            what_vtk: a string list to specify which vtk to generate. the string can be "path", "gesture" or so on.
            vtk_path: the path for VTK file
        '''
        if what_vtk == "gesture":
            # get the gesture data and delete records with the LLA is 0
            index_ges = np.where(self.gesture_data[:, 2] == 0)
            self.gesture_data = np.delete(self.gesture_data, index_ges, axis=0)
            if len(self.gesture_data) == 0:
                raise Exception("no gesture data generated, no gesture VTP file generated")
            self.__gen_gesture_vtp(self.gesture_data, vtk_path)
        elif what_vtk == "path":
            index_path = np.where(self.path_data[:, 2] == 0)
            self.path_data = np.delete(self.path_data, index_path, axis=0)
            if len(self.path_data) == 0:
                raise Exception("no path data generated, no path VTP file generated")
            self.__gen_path_vtp(self.path_data, vtk_path)
        else:
            raise TypeError(
                'please type the correct type vtk file, path or gesture')

    # @jit
    def get_path_gesture_data(self):
        '''
        return path and gesture data, the length of path data must be the same with the length of gesture data.
         gesture_data: numpy array nx12, [x, y, z, pos_xaxis_x, pos_xaxis_y, pos_xaxis_z, pos_yaxis_x, pos_yaxis_y,
                                pos_yaxis_z, pos_zaxis_x, pos_zaxis_y, pos_zaxis_z]
        unit_vector_coord: numpy array nx9 [unit_xaxis_x, unit_xaxis_y, unit_xaxis_z, unit_yaxis_x, unit_yaxis_y,
                                unit_yaxis_z, unit_zaxis_x, unit_zaxis_y, unit_zaxis_z]
        returns:
              gesture_on_path_data: numpy array nx21, [x, y, z, unit_xaxis_x, unit_xaxis_y, unit_xaxis_z, unit_yaxis_x,
                        unit_yaxis_y, unit_yaxis_z, unit_zaxis_x, unit_zaxis_y, unit_zaxis_z, pos_xaxis_x, pos_xaxis_y,
                        pos_xaxis_z, pos_yaxis_x, pos_yaxis_y, pos_yaxis_z, pos_zaxis_x, pos_zaxis_y, pos_zaxis_z]
        '''
        if len(self.gesture_data) == 0:
            raise Exception("gesture data is empty, could not return gesture data")
        if len(self.path_data) == 0:
            raise Exception("path data is empty, could not return gesture data")
        if len(self.unit_vector_coord) == 0:
            raise Exception("gesture data is empty, could not return gesture data")
        if len(self.gesture_data) != len(self.path_data) or len(self.gesture_data) != len(self.unit_vector_coord) \
                or len(self.path_data) != len(self.unit_vector_coord):
            raise Exception("gesture data is not equal to path data and unit vector coord data,\
             could not return gesture data")
        # merge all data together and delete records with the LLA is 0(z==0 in path data)
        gesture_on_path_data = np.zeros((len(self.path_data), 21))
        gesture_on_path_data[:, 0:3] = self.path_data
        gesture_on_path_data[:, 3:12] = self.unit_vector_coord
        gesture_on_path_data[:, 12:21] = self.gesture_data[:, 3:12]
        # delete LLA is 0 records
        index_path = np.where(gesture_on_path_data[:, 2] == 0)
        gesture_on_path_data = np.delete(gesture_on_path_data, index_path, axis=0)
        if len(gesture_on_path_data) == 0:
            raise Exception("LLA is all zeros, could not return gesture data")
        return gesture_on_path_data

    def __read_euler_from_csv(self):
        # check the euler file header
        if [i.strip() for i in self.eul_header] != self.euler_column:
            raise ValueError("euler file must have the header ('Yaw_deg', 'Pitch_deg', 'Roll_deg'),\
             please check the euler file")

    def __euler_to_gesture(self):
        '''
         get the euler angles of each record and generate each coordinate for each unit Vector rotation axis(x,y,z).
        '''
        # convert deg to rad
        euler_data = self.euler_data * np.pi / 180.0
        for i in range(euler_data.shape[0]):
            # convert euler to quaternion
            if np.linalg.norm(euler_data[i, :]) < threhold_angle * math.pi / 180:  # %5*pi/180
                self.quat[i, :] = [1, 0, 0, 0]
            else:
                self.quat[i, :] = self.__euler2quat(euler_data[i, :])
            if i == 0:
                self.Quat[i, :] = self.quat[i, :]
            else:
                self.Quat[i, :] = self.__quat_multiply(self.Quat[i - 1, :], self.quat[i, :])
            self.unit_vector_coord[i, 0:3] = self.__quat2dcm(self.Quat[i, :])[:, 0]
            self.unit_vector_coord[i, 3:6] = self.__quat2dcm(self.Quat[i, :])[:, 1]
            self.unit_vector_coord[i, 6:9] = self.__quat2dcm(self.Quat[i, :])[:, 2]

    def __quat2dcm(self, q):
        """
        Convert quaternion to direction cosine matrix
        Args:
            q: quaternion, [q0, q1, q2, q3], q0 is the scalar
        Return:
            dcm: direction cosine matrix
        """
        q0q0 = q[0] * q[0]
        q0q1 = q[0] * q[1]
        q0q2 = q[0] * q[2]
        q0q3 = q[0] * q[3]
        q1q1 = q[1] * q[1]
        q1q2 = q[1] * q[2]
        q1q3 = q[1] * q[3]
        q2q2 = q[2] * q[2]
        q2q3 = q[2] * q[3]
        q3q3 = q[3] * q[3]
        dcm = np.zeros((3, 3))
        dcm[0, 0] = q0q0 + q1q1 - q2q2 - q3q3
        dcm[0, 1] = 2.0 * (q1q2 + q0q3)
        dcm[0, 2] = 2.0 * (q1q3 - q0q2)
        dcm[1, 0] = 2.0 * (q1q2 - q0q3)
        dcm[1, 1] = q0q0 - q1q1 + q2q2 - q3q3
        dcm[1, 2] = 2.0 * (q2q3 + q0q1)
        dcm[2, 0] = 2.0 * (q1q3 + q0q2)
        dcm[2, 1] = 2.0 * (q2q3 - q0q1)
        dcm[2, 2] = q0q0 - q1q1 - q2q2 + q3q3
        return dcm

    def __euler2quat(self, angles, rot_seq='zyx'):
        '''
        Convert Euler angles to quaternion.
        Args:
            angles: 3x1 Euler angles, rad.
            rot_seq: rotation sequence corresponding to the angles.
        Return:
            q: quaternion, [q0, q1, q2, q3], q0 is the scalar
        """
        '''
        cangle = np.cos(0.5 * angles)
        sangle = np.sin(0.5 * angles)
        rot_seq = rot_seq.lower()
        if rot_seq == 'zyx':
            return np.array([cangle[0] * cangle[1] * cangle[2] + sangle[0] * sangle[1] * sangle[2],
                             cangle[0] * cangle[1] * sangle[2] - sangle[0] * sangle[1] * cangle[2],
                             cangle[0] * sangle[1] * cangle[2] + sangle[0] * cangle[1] * sangle[2],
                             sangle[0] * cangle[1] * cangle[2] - cangle[0] * sangle[1] * sangle[2]])
        elif rot_seq == 'zyz':
            return np.array([cangle[0] * cangle[1] * cangle[2] - sangle[0] * cangle[1] * sangle[2],
                             cangle[0] * sangle[1] * sangle[2] - sangle[0] * sangle[1] * cangle[2],
                             cangle[0] * sangle[1] * cangle[2] + sangle[0] * sangle[1] * sangle[2],
                             sangle[0] * cangle[1] * cangle[2] + cangle[0] * cangle[1] * sangle[2]])
        elif rot_seq == 'zxy':
            return np.array([cangle[0] * cangle[1] * cangle[2] - sangle[0] * sangle[1] * sangle[2],
                             cangle[0] * sangle[1] * cangle[2] - sangle[0] * cangle[1] * sangle[2],
                             cangle[0] * cangle[1] * sangle[2] + sangle[0] * sangle[1] * cangle[2],
                             cangle[0] * sangle[1] * sangle[2] + sangle[0] * cangle[1] * cangle[2]])
        elif rot_seq == 'zxz':
            return np.array([cangle[0] * cangle[1] * cangle[2] - sangle[0] * cangle[1] * sangle[2],
                             cangle[0] * sangle[1] * cangle[2] + sangle[0] * sangle[1] * sangle[2],
                             sangle[0] * sangle[1] * cangle[2] - cangle[0] * sangle[1] * sangle[2],
                             cangle[0] * cangle[1] * sangle[2] + sangle[0] * cangle[1] * cangle[2]])
        elif rot_seq == 'yxz':
            return np.array([cangle[0] * cangle[1] * cangle[2] + sangle[0] * sangle[1] * sangle[2],
                             cangle[0] * sangle[1] * cangle[2] + sangle[0] * cangle[1] * sangle[2],
                             sangle[0] * cangle[1] * cangle[2] - cangle[0] * sangle[1] * sangle[2],
                             cangle[0] * cangle[1] * sangle[2] - sangle[0] * sangle[1] * cangle[2]])
        elif rot_seq == 'yxy':
            return np.array([cangle[0] * cangle[1] * cangle[2] - sangle[0] * cangle[1] * sangle[2],
                             cangle[0] * sangle[1] * cangle[2] + sangle[0] * sangle[1] * sangle[2],
                             sangle[0] * cangle[1] * cangle[2] + cangle[0] * cangle[1] * sangle[2],
                             cangle[0] * sangle[1] * sangle[2] - sangle[0] * sangle[1] * cangle[2]])
        elif rot_seq == 'yzx':
            return np.array([cangle[0] * cangle[1] * cangle[2] - sangle[0] * sangle[1] * sangle[2],
                             cangle[0] * cangle[1] * sangle[2] + sangle[0] * sangle[1] * cangle[2],
                             cangle[0] * sangle[1] * sangle[2] + sangle[0] * cangle[1] * cangle[2],
                             cangle[0] * sangle[1] * cangle[2] - sangle[0] * cangle[1] * sangle[2]])
        elif rot_seq == 'yzy':
            return np.array([cangle[0] * cangle[1] * cangle[2] - sangle[0] * cangle[1] * sangle[2],
                             sangle[0] * sangle[1] * cangle[2] - cangle[0] * sangle[1] * sangle[2],
                             cangle[0] * cangle[1] * sangle[2] + sangle[0] * cangle[1] * cangle[2],
                             cangle[0] * sangle[1] * cangle[2] + sangle[0] * sangle[1] * sangle[2]])
        elif rot_seq == 'xyz':
            return np.array([cangle[0] * cangle[1] * cangle[2] - sangle[0] * sangle[1] * sangle[2],
                             cangle[0] * sangle[1] * sangle[2] + sangle[0] * cangle[1] * cangle[2],
                             cangle[0] * sangle[1] * cangle[2] - sangle[0] * cangle[1] * sangle[2],
                             cangle[0] * cangle[1] * sangle[2] + sangle[0] * sangle[1] * cangle[2]])
        elif rot_seq == 'xyx':
            return np.array([cangle[0] * cangle[1] * cangle[2] - sangle[0] * cangle[1] * sangle[2],
                             cangle[0] * cangle[1] * sangle[2] + sangle[0] * cangle[1] * cangle[2],
                             cangle[0] * sangle[1] * cangle[2] + sangle[0] * sangle[1] * sangle[2],
                             sangle[0] * sangle[1] * cangle[2] - cangle[0] * sangle[1] * sangle[2]])
        elif rot_seq == 'xzy':
            return np.array([cangle[0] * cangle[1] * cangle[2] + sangle[0] * sangle[1] * sangle[2],
                             sangle[0] * cangle[1] * cangle[2] - cangle[0] * sangle[1] * sangle[2],
                             cangle[0] * cangle[1] * sangle[2] - sangle[0] * sangle[1] * cangle[2],
                             cangle[0] * sangle[1] * cangle[2] + sangle[0] * cangle[1] * sangle[2]])
        elif rot_seq == 'xzx':
            return np.array([cangle[0] * cangle[1] * cangle[2] - sangle[0] * cangle[1] * sangle[2],
                             cangle[0] * cangle[1] * sangle[2] + sangle[0] * cangle[1] * cangle[2],
                             cangle[0] * sangle[1] * sangle[2] - sangle[0] * sangle[1] * cangle[2],
                             cangle[0] * sangle[1] * cangle[2] + sangle[0] * sangle[1] * sangle[2]])
        else:
            return False

    def __quat_multiply(self, q1, q2):
        """
        Multiplication of two quaternions
        Args:
            q1: quaternion, scalar first
            q2: quaternion, scalar first
        Returns:
            q = q1 * q2
        """
        q = np.array([0.0, 0.0, 0.0, 0.0])
        q[0] = q1[0] * q2[0] - q1[1] * q2[1] - q1[2] * q2[2] - q1[3] * q2[3]
        q[1] = q1[0] * q2[1] + q1[1] * q2[0] + q1[2] * q2[3] - q1[3] * q2[2]
        q[2] = q1[0] * q2[2] - q1[1] * q2[3] + q1[2] * q2[0] + q1[3] * q2[1]
        q[3] = q1[0] * q2[3] + q1[1] * q2[2] - q1[2] * q2[1] + q1[3] * q2[0]
        return q

    def __gesture_for_path(self, num):
        '''
        get the actual gesture data by adding ecef position data
        '''
        if len(self.pos_data) == 0:
            print(" could not generate the gesture data as the position file is empty")
        elif len(self.path_data) != len(self.unit_vector_coord) or len(self.pos_data) != len(self.euler_data):
            print("could not generate the gesture data as the length of position file is not equal to euler file's ")
        else:
            self.gesture_data[:, 0:3] = self.path_data[:, 0:3]
            self.gesture_data[:, 3:6] = self.path_data[:, 0:3] + self.unit_vector_coord[:, 0:3] * num
            self.gesture_data[:, 6:9] = self.path_data[:, 0:3] + self.unit_vector_coord[:, 3:6] * num
            self.gesture_data[:, 9:12] = self.path_data[:, 0:3] + self.unit_vector_coord[:, 6:9] * num

    def __read_pos_from_csv(self):
        # check the pos file header
        if [i.strip() for i in self.pos_header] != self.pos_column:
            raise ValueError("pos file must have the header['pos_lat (deg)', 'pos_lon (deg)', 'pos_alt (m)'], \
             please check the position file")

    def __gps_to_ecef(self):
        # convert deg to rad for lat, lon
        convert_pos_data = self.pos_data
        convert_pos_data[:, 0] = self.pos_data[:, 0] * D2R
        convert_pos_data[:, 1] = self.pos_data[:, 1] * D2R
        # store the ecef xyz position into coordinate array
        ecef_pos = self.__lla2ecef_batch(convert_pos_data)
        self.path_data[:, 0] = ecef_pos[:, 0]
        self.path_data[:, 1] = ecef_pos[:, 1]
        self.path_data[:, 2] = ecef_pos[:, 2]

        # np.savetxt('output_file/ecef_pos.csv', self.path_data, delimiter=',', header="x, y, z", comments='')

    def __lla2ecef_batch(self, lla):
        '''
         convert the LLA coordinate [Lat Lon Alt] position to xyz ecef position
        args:
            lla: GPS LLA position  [Lat, Lon, Alt], [rad, rad, meter], nx3 numpy array
        :return:
            ecef_xyz: ecef position, nx3 numpy array
        '''

        # only one LLA
        if lla.ndim == 1:
            return self.__lla2ecef(lla)
        # multiple LLA
        n = lla.shape[0]
        ecef_xyz = np.zeros((n, 3))
        for i in range(0, n):
            sl = math.sin(lla[i, 0])
            cl = math.cos(lla[i, 0])
            sl_sqr = sl * sl
            r = Re / math.sqrt(1.0 - E_SQR * sl_sqr)
            rho = (r + lla[i, 2]) * cl

            ecef_xyz[i, 0] = rho * math.cos(lla[i, 1])
            ecef_xyz[i, 1] = rho * math.sin(lla[i, 1])
            ecef_xyz[i, 2] = (r * (1.0 - E_SQR) + lla[i, 2]) * sl
        return ecef_xyz

    def __lla2ecef(self, lla):
        '''
         convert the LLA coordinate [Lat Lon Alt] position to xyz ecef position
        Args:
            lla: [Lat, Lon, Alt], [rad, rad, meter], numpy array of size (3,)
        return:
            ecef_xyz: ecef position, nx3 numpy array
        '''
        sl = math.sin(lla[0])
        cl = math.cos(lla[0])
        sl_sqr = sl * sl

        r = Re / math.sqrt(1.0 - E_SQR * sl_sqr)
        rho = (r + lla[2]) * cl
        x = rho * math.cos(lla[1])
        y = rho * math.sin(lla[1])
        z = (r * (1.0 - E_SQR) + lla[2]) * sl
        return np.array([x, y, z])

    def __gen_gesture_vtp(self, path_gesture_data, vtk_path):
        '''
          generate gesture vtp file format dependent on time for paraview
        agrs:
            path_gesture_data: nx12 numpy array, contains
                        [x, y, z, pos_xaxis_x, pos_xaxis_y, pos_xaxis_z, pos_yaxis_x, pos_yaxis_y,
                        pos_yaxis_z, pos_zaxis_x, pos_zaxis_y, pos_zaxis_z]
            vtk_path: string, the stored gesture vtp files path and file name

        '''
        number_of_steps = path_gesture_data.shape[0]
        writer = vtk.vtkXMLPolyDataWriter()
        data_to_write = vtk.vtkPolyData()
        writer.SetNumberOfTimeSteps(number_of_steps)
        writer.SetInputData(data_to_write)
        writer.SetFileName(vtk_path)
        writer.Start()
        for i in range(number_of_steps):
            # 每个姿态图就是一个ployData
            linepoly = vtk.vtkPolyData()
            # 每个姿态图上有四个点
            each_ges_points = vtk.vtkPoints()
            each_ges_points.SetNumberOfPoints(4)
            each_ges_points.SetPoint(0, path_gesture_data[i, 0], path_gesture_data[i, 1], path_gesture_data[i, 2])
            for j in range(1, 4):
                each_ges_points.SetPoint(j, path_gesture_data[i, 3 * j], path_gesture_data[i, 3 * j + 1],
                                         path_gesture_data[i, 3 * j + 2])
            linepoly.SetPoints(each_ges_points)
            # 三个方向上的姿态线为一个cell
            lines = vtk.vtkCellArray()
            # x 方向上的姿态线
            line0 = vtk.vtkLine()
            line0.GetPointIds().SetId(0, 0)
            line0.GetPointIds().SetId(1, 1)
            # y 方向上的姿态线
            line1 = vtk.vtkLine()
            line1.GetPointIds().SetId(0, 0)
            line1.GetPointIds().SetId(1, 2)
            # z 方向上的姿态线
            line2 = vtk.vtkLine()
            line2.GetPointIds().SetId(0, 0)
            line2.GetPointIds().SetId(1, 3)
            lines.InsertNextCell(line0)
            lines.InsertNextCell(line1)
            lines.InsertNextCell(line2)
            # setup colors
            colors = vtk.vtkNamedColors()
            Colors = vtk.vtkUnsignedCharArray()
            Colors.SetNumberOfComponents(3)
            Colors.SetName("Colors")
            Colors.InsertNextTypedTuple(colors.GetColor3ub("red"))
            Colors.InsertNextTypedTuple(colors.GetColor3ub("yellow"))
            Colors.InsertNextTypedTuple(colors.GetColor3ub("green"))
            linepoly.SetLines(lines)
            linepoly.GetCellData().SetScalars(Colors)
            data_to_write.ShallowCopy(linepoly)
            writer.WriteNextTime(i)
        writer.Stop()
        print("gesture vtp file is generated!")

    def __gen_path_vtp(self, path_gesture_data, vtk_path):
        '''
         generate points into VTP file for paraview
         args:
            path_gesture_data: nx12 numpy array, contains
                        [x, y, z, pos_xaxis_x, pos_xaxis_y, pos_xaxis_z, pos_yaxis_x, pos_yaxis_y, pos_yaxis_z,
                        pos_zaxis_x, pos_zaxis_y, pos_zaxis_z]
            vtk_path: string, the stored path vtp files path and file name
        '''
        number_of_steps = path_gesture_data.shape[0]
        points = vtk.vtkPoints()
        points.SetNumberOfPoints(number_of_steps)
        # Create the topology of the point (a vertex)
        vertices = vtk.vtkCellArray()
        vertices.InsertNextCell(number_of_steps)
        for i in range(number_of_steps):
            points.SetPoint(i, path_gesture_data[i, 0], path_gesture_data[i, 1], path_gesture_data[i, 2])
            # We need an an array of point id's for InsertNextCell.
            vertices.InsertCellPoint(i)
        polydata = vtk.vtkPolyData()
        polydata.SetPoints(points)
        polydata.SetLines(vertices)
        namedColors = vtk.vtkNamedColors()
        colors = vtk.vtkUnsignedCharArray()
        colors.SetNumberOfComponents(3)
        colors.InsertNextTypedTuple(namedColors.GetColor3ub("white"))
        polydata.GetCellData().SetScalars(colors)
        writer = vtk.vtkXMLPolyDataWriter()
        writer.SetFileName(vtk_path)
        writer.SetInputData(polydata)
        writer.Write()
        print("path VTP file is generated!")

