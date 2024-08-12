#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import nibabel as nib
import numpy as np

def create_zero_displacement(fixed_path, moving_path):
    moving_nib = nib.load(moving_path)
    moving_array = moving_nib.get_fdata()
    D, H, W = moving_array.shape
    return np.zeros((D, H, W, 3))

input_dir = '/input/'
output_dir = '/output/'

fixed_mod = '0000'
moving_mod = '0001'

# select inference cases
list_case = sorted([k.split('_')[1] for k in os.listdir(input_dir) if f'{moving_mod}.nii.gz' in k])
print(f"Number total cases: {len(list_case)}")

for case in list_case:
    # Load image using SimpleITK
    fixed_path = os.path.join(input_dir, f"ReMIND2Reg_{case}_{fixed_mod}.nii.gz")
    moving_path = os.path.join(input_dir, f"ReMIND2Reg_{case}_{moving_mod}.nii.gz") 
    
    # Create displacement field in voxel grid
    dsplcmt_fld_pxl = create_zero_displacement(fixed_path=fixed_path, moving_path=moving_path)

    # Saving displacement field in voxel
    dis_filnm = os.path.join(output_dir, f'disp_{case}_{fixed_mod}_{case}_{moving_mod}.nii.gz')
    affine_img = nib.load(moving_path).affine
    disp_field_img = nib.Nifti1Image(dsplcmt_fld_pxl.astype(np.float32), affine_img)
    disp_field_img.to_filename(dis_filnm)

   