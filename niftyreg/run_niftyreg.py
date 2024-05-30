import os
import numpy as np
import SimpleITK as sitk
from scipy.ndimage import map_coordinates
import nibabel as nib

FLIPXY_44 = np.diag([-1, -1, 1, 1])

def clean_cmdline(cmd):
    return cmd.replace(' ', '\ ').replace('(','\(').replace(')','\)')

def _to_itk_convention(matrix):
    """RAS to LPS"""
    matrix = np.dot(FLIPXY_44, matrix)
    matrix = np.dot(matrix, FLIPXY_44)
    matrix = np.linalg.inv(matrix)
    return matrix

def _matrix_to_itk_transform(matrix, dimensions=3):
    matrix = _to_itk_convention(matrix)
    rotation = matrix[:dimensions, :dimensions].ravel().tolist()
    translation = matrix[:dimensions, 3].tolist()
    transform = sitk.AffineTransform(rotation, translation)
    return transform


def create_displacement_field(matrix, mov_img):
    """The nitfy file contains the matrix from floating to reference."""
    transform = _matrix_to_itk_transform(matrix)
    disp_field_space = sitk.TransformToDisplacementField(
                transform,
                sitk.sitkVectorFloat64,
                mov_img.GetSize(),
                mov_img.GetOrigin(),
                mov_img.GetSpacing(),
                mov_img.GetDirection(),
            )
    disp_field_space = sitk.GetArrayFromImage(disp_field_space)
    disp_field_space *= np.array([-1, -1, 1]) # RAS
    disp_field_space = disp_field_space.transpose(2,1,0,3) # Convention sitk
    return disp_field_space, transform
    # sitk.WriteImage(displacement_field, disp_path)
    
def get_mask(ref):
    ref_data = sitk.GetArrayFromImage(ref).astype(np.float32)
    img_data = (ref_data>0).astype(np.float32)
    output = sitk.GetImageFromArray(img_data)
    output.CopyInformation(ref)
    output =  sitk.Cast(output, sitk.sitkFloat32)
    return output 

validation_cases = ['0098', '0099', '0100', '0101', '0102']
reg_directions = [
    {'moving':'0001', 'fixed':'0000'},
    {'moving':'0002', 'fixed':'0000'},
                ]
path_data = '/Users/reubendo/Documents/repo/Learn2RegChallenge/ReMIND2Reg/imagesTr'
path_output = './output'
for dir in ['niftyreg', 'mask', 'disp']:
    os.makedirs(os.path.join(path_output, dir), exist_ok=True)

from nibabel.affines import apply_affine

for case in validation_cases:
    for reg_direction in reg_directions:
        fixed_mod = reg_direction["fixed"]
        moving_mod = reg_direction["moving"]
        
        # Running NiftyReg 
        
        ### Creating Masks: load images, create masks, save masks       
        fixed_path = os.path.join(path_data, f"ReMIND2Reg_{case}_{fixed_mod}.nii.gz") 
        fixed_img = sitk.ReadImage(fixed_path)
        fixed_mask = get_mask(fixed_img)
        fixed_mask_flnm = os.path.join(path_output, 'mask', f'ReMIND2Reg_{case}_{fixed_mod}_mask.nii.gz')
        sitk.WriteImage(fixed_mask, fixed_mask_flnm)
        
        moving_path = os.path.join(path_data, f"ReMIND2Reg_{case}_{moving_mod}.nii.gz") 
        moving_img = sitk.ReadImage(moving_path)
        moving_mask = get_mask(moving_img)
        moving_mask_flnm = os.path.join(path_output, 'mask', f'ReMIND2Reg_{case}_{moving_mod}_mask.nii.gz')
        sitk.WriteImage(moving_mask, moving_mask_flnm)
        

        ### Excecuting NiftyReg        
        res_filnm = os.path.join(path_output, 'niftyreg', f'ReMIND2Reg_{case}_{fixed_mod}_{case}_{moving_mod}.txt')
        res_img = os.path.join(path_output, 'niftyreg', f'ReMIND2Reg_{case}_{moving_mod}_reg.nii.gz')
        p = "reg_aladin -ref {} -flo {} -rmask {} -fmask {} -noSym -aff {} -res {} -nac -ln 2 -lp 10"
        os.system(p.format(
            clean_cmdline(fixed_path),
            clean_cmdline(moving_path),
            clean_cmdline(fixed_mask_flnm),
            clean_cmdline(moving_mask_flnm),
            clean_cmdline(res_filnm), 
            clean_cmdline(res_img)
            )
        )
        
        # Saving transformation affine as displacement field
        
        ### Create displacement field in space (mm) RAS
        affine_nifti =  np.loadtxt(res_filnm)
        affine_ras = np.linalg.inv(affine_nifti)
        disp_field_space, transform = create_displacement_field(affine_ras, moving_img)
        
        ### Creating displacement field in voxel 
        moving_nib = nib.load(moving_path)
        affine_img = moving_nib.affine
        moving_array = moving_nib.get_fdata()
        
        D, H, W = moving_array.shape
        identity = np.meshgrid(np.arange(D), np.arange(
            H), np.arange(W), indexing='ij')
        identity_voxel = np.stack(identity,-1)
        identity_space = apply_affine(affine_img, identity_voxel)
        new_space = disp_field_space + identity_space 
        disp_field_voxel = apply_affine(np.linalg.inv(affine_img), new_space) - identity_voxel
        
        ### Saving displacement field in voxel
        dis_filnm = os.path.join(path_output, 'disp', f'disp_{case}_{fixed_mod}_{case}_{moving_mod}.nii.gz')
        disp_field_img = nib.Nifti1Image(disp_field_voxel.astype(np.float32), affine_img)
        disp_field_img.to_filename(dis_filnm)
        
        ### Testing
        # Check for L2R evaluation
        disp_field_voxel = nib.load(dis_filnm).get_fdata()
        identity = np.meshgrid(np.arange(D), np.arange(
            H), np.arange(W), indexing='ij')
        moving_warped = map_coordinates(
            moving_array, identity + disp_field_voxel.transpose(3,0,1,2), order=0)
        moving_warped_nib = nib.Nifti1Image(moving_warped, affine_img)
        res_img_scipy = os.path.join(path_output, 'disp', f'ReMIND2Reg_{case}_{moving_mod}_reg_dis.nii.gz')
        moving_warped_nib.to_filename(res_img_scipy)

        # Check for SimpleITK vs Niftyreg
        res_img_simpleitk = os.path.join(path_output, 'disp', f'ReMIND2Reg_{case}_{moving_mod}_reg_sitk.nii.gz')
        new = sitk.Resample(moving_img, moving_img, transform)
        sitk.WriteImage(new, res_img_simpleitk)
        
        
        


