# ReMIND2Reg: Brain Resection Multimodal Registration

This official repository houses baseline methods, training scripts, and pretrained models for the ReMIND2Reg challenge at Learn2Reg 2025.
The challenge is dedicated to unsupervised brain pre-operative MR to intraoperative ultrasound image registration.

Please visit https://learn2reg.grand-challenge.org/ for more information.

![glioma_example](https://github.com/ReubenDo/ReMIND2Reg/blob/main/imgs/remind2reg.gif)*(a) Contrast-enhanced T1 and post-resection intra-operative US; (b) T2 and post-resection intra-operative US.*



**Training/Validation:** [Download](https://zenodo.org/records/11387725) 

**Context:** Surgical resection is the critical first step for treating most brain tumors, and the extent of resection is the major modifiable determinant of patient outcome. Neuronavigation has helped considerably in providing intraoperative guidance to surgeons, allowing them to visualize the location of their surgical instruments relative to the tumor and critical brain structures visible in preoperative MRI. However, the utility of neuronavigation decreases as surgery progresses due to brain shift, which is caused by brain deformation and tissue resection during surgery, leaving surgeons without guidance. To compensate for brain shift, we propose to perform image registration using 3D intraoperative ultrasound.

**Objectives:** The goal of the ReMIND2Reg challenge task is to register multi-parametric pre-operative MRI and intra-operative 3D ultrasound images. Specifically, we focus on the challenging problem of pre-operative to post-resection registration, requiring the estimation of large deformations and tissue resections. Preoperative MRI comprises two structural MRI sequences: contrast-enhanced T1-weighted (ceT1) and native T2-weighted (T2). However, not all sequences will be available for all cases. For this reason, developed methods must have the flexibility to leverage either ceT1 or T2 images at inference time. To tackle this challenging registration task, we provide a large non-annotated training set (N=158 pairs US/MR). Model development is performed on annotated validation sets (N=10 pairs US/MR). The final evaluation will be performed on a private test set using Docker (more details will be provided later). The task is to find one solution for the registration of two pairs of images per patient:
- 3D post-resection iUS (fixed) and ceT1 (moving).
- 3D post-resection iUS (fixed) and T2 (moving).

**Dataset:** The ReMIND2Reg dataset is a pre-processed subset of the ReMIND dataset, which contains pre- and intra-operative data collected on consecutive patients who were surgically treated with image-guided tumor resection between 2018 and 2024 at the Brigham and Women’s Hospital (Boston, USA). The training (N=99) and validation (N=5) cases correspond to a subset of the public version of the ReMIND dataset. Specifically, the training set includes images of 99 patients with 99 3D iUS, 93 ceT1, and 62 T2 and validation images of 5 patients with 5 3D US, 5 ceT1, and 5 T2. The images are paired as described above with one or two image pairs per patient, resulting in 155 image pairs for training and 10 image pairs for validation. The test cases are not publicly available and will remain private. For details on the image acquisition (scanner details, etc.), please see https://doi.org/10.1101/2023.09.14.23295596 

Number of registration pairs: Training: 155, Validation: 10, Test: 20.

**Pre-Processing:** All images are converted to NIfTI. When more than one pre-operative MR sequence was available, ceT1 was affinely co-registered to the T2 using NiftyReg; Ultrasound images were resampled in the pre-operative MR space. Images were cropped in the field of view of the iUS in an image size of 256x256x256 with a spacing of 0.5x0.5x0.5mm.

**Citation:**  Juvekar, P., Dorent, R., Kögl, F., Torio, E., Barr, C., Rigolo, L., Galvin, C., Jowkar, N., Kazi, A., Haouchine, N., Cheema, H., Navab, N., Pieper, S., Wells, W. M., Bi, W. L., Golby, A., Frisken, S., & Kapur, T. (2023). The Brain Resection Multimodal Imaging Database (ReMIND). Nature Scientific Data. https://doi.org/10.1101/2023.09.14.23295596
