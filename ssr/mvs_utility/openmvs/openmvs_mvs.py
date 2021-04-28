import os
import subprocess
import shutil
from ssr.utility.logging_extension import logger
from ssr.config.ssr_config import SSRConfig


class OpenMVSReconstructor:
    def __init__(self):
        self.ssr_config = SSRConfig.get_instance()
        self.openmvs_bin_dp = self.ssr_config.get_option_value(
            "openmvs_bin_dp", str
        )
        self.interface_visualsfm_fp = os.path.join(
            self.openmvs_bin_dp, "InterfaceVisualSFM"
        )
        self.interface_colmap_fp = os.path.join(
            self.openmvs_bin_dp, "InterfaceCOLMAP"
        )
        self.densify_point_cloud_fp = os.path.join(
            self.openmvs_bin_dp,
            "DensifyPointCloud",
        )
        self.reconstruct_mesh_fp = os.path.join(
            self.openmvs_bin_dp, "ReconstructMesh"
        )
        self.refine_mesh_fp = os.path.join(self.openmvs_bin_dp, "RefineMesh")
        self.texture_mesh_fp = os.path.join(self.openmvs_bin_dp, "TextureMesh")

    # File Format of OpenMVS
    # https://github.com/cdcseacave/openMVS/blob/master/libs/MVS/Interface.h
    # https://github.com/cdcseacave/openMVS/blob/develop/apps/InterfaceOpenMVG/InterfaceOpenMVG.cpp
    # https://github.com/cdcseacave/openMVS/blob/develop/apps/InterfaceVisualSFM/InterfaceVisualSFM.cpp

    def convert_visualsfm_to_openMVS(
        self, nvm_ifp, image_idp, openmvs_workspace_temp, openmvs_ofp
    ):

        logger.info("convert_visualsfm_to_openMVS: ...")

        for possible_img_file in os.listdir(image_idp):
            img_ifp = os.path.join(image_idp, possible_img_file)
            img_ofp = os.path.join(openmvs_workspace_temp, possible_img_file)
            if os.path.isfile(img_ifp) and not os.path.isfile(img_ofp):
                shutil.copyfile(img_ifp, img_ofp)

        # InterfaceVisualSFM scene.nvm
        visualsfm_to_openmvs_call = [
            self.interface_visualsfm_fp,
            "-i",
            nvm_ifp,
            "-w",
            openmvs_workspace_temp,
            "-o",
            openmvs_ofp,
        ]

        logger.info(str(visualsfm_to_openmvs_call))
        visualsfm_to_openmvs_proc = subprocess.Popen(visualsfm_to_openmvs_call)
        visualsfm_to_openmvs_proc.wait()
        logger.info("convert_visualsfm_to_openMVS: Done")

    def convert_colmap_to_openMVS(
        self,
        colmap_dense_idp,
        openmvs_workspace_dp,
        openmvs_ofn,
        image_folder="images/",
        lazy=False,
    ):

        # logger.info('convert_colmap_to_openMVS: ...')
        openmvs_ofp = os.path.join(openmvs_workspace_dp, openmvs_ofn)
        if not os.path.isfile(openmvs_ofp) or not lazy:
            colmap_to_openmvs_call = [
                self.interface_colmap_fp,
                "-i",
                colmap_dense_idp,
                "--image-folder",
                image_folder,
                "-w",
                openmvs_workspace_dp,
                "-o",
                openmvs_ofn,
            ]

            logger.info(str(colmap_to_openmvs_call))
            colmap_to_openmvs_proc = subprocess.Popen(colmap_to_openmvs_call)
            colmap_to_openmvs_proc.wait()
        # logger.info('convert_colmap_to_openMVS: Done')

    def densify_point_cloud(
        self, openmvs_workspace_dp, openmvs_ifn, openmvs_ofn, lazy=False
    ):
        logger.info("densify_point_cloud: ...")

        # The workspace folder defined by "-w"
        # MUST BE THE FOLDER WHICH CONTAINS THE *.mvs file

        if (
            not os.path.isfile(os.path.join(openmvs_workspace_dp, openmvs_ofn))
            or not lazy
        ):
            densify_point_cloud_call = [
                self.densify_point_cloud_fp,
                "-i",
                openmvs_ifn,
                "-w",
                openmvs_workspace_dp,
                "-o",
                openmvs_ofn,
            ]

            logger.info(str(densify_point_cloud_call))
            densify_proc = subprocess.Popen(densify_point_cloud_call)
            densify_proc.wait()
        logger.info("densify_point_cloud: Done ")

    def reconstruct_mesh(
        self,
        openmvs_workspace_dp,
        openmvs_ifn,
        openmvs_ofn,
        lazy=False,
        # Reconstruction option
        min_point_distance=None,  # OpenMVS Default Value: 2.5
        # Clean options:
        decimate_value=None,  # OpenMVS Default Value: 1.0
        smoothing_iterations=None,  # OpenMVS Default Value: 2
        # Hidden options
        mesh_ifp=None,
        mesh_export=None,
    ):

        # See:
        # https://github.com/cdcseacave/openMVS/blob/develop/apps/ReconstructMesh/ReconstructMesh.cpp
        # and
        # bin/OpenMVS/ReconstructMesh --help
        #
        # Uses image information for mesh computation
        # Uses Delaunay triangulation
        #     From the log
        #         Delaunay tetrahedras weighting completed: ...
        #         Delaunay tetrahedras graph-cut completed ...

        # logger.info('reconstruct_mesh: ...')
        if (
            not os.path.isfile(os.path.join(openmvs_workspace_dp, openmvs_ofn))
            or not lazy
        ):
            reconstruct_mesh_call = [
                self.reconstruct_mesh_fp,
                "-i",
                openmvs_ifn,
                "-w",
                openmvs_workspace_dp,
                "-o",
                openmvs_ofn,
            ]
            # Reconstruction option
            if min_point_distance is not None:
                reconstruct_mesh_call += [
                    "--min-point-distance",
                    str(min_point_distance),
                ]
            # Clean options:
            if decimate_value is not None:
                reconstruct_mesh_call += ["--decimate", str(decimate_value)]
            if smoothing_iterations is not None:
                reconstruct_mesh_call += [
                    "--smooth",
                    str(smoothing_iterations),
                ]
            # Hidden option
            # https://github.com/cdcseacave/openMVS/blob/master/apps/ReconstructMesh/ReconstructMesh.cpp
            if mesh_ifp is not None:
                reconstruct_mesh_call += ["--mesh-file", mesh_ifp]
            if mesh_export is not None:
                reconstruct_mesh_call += [
                    "--mesh-export",
                    str(int(mesh_export)),
                ]
            logger.info(str(reconstruct_mesh_call))
            reconstruct_proc = subprocess.Popen(reconstruct_mesh_call)
            reconstruct_proc.wait()

        # logger.info('reconstruct_mesh: Done')

    def refine_mesh(
        self,
        openmvs_workspace_dp,
        openmvs_ifn,
        openmvs_ofn,
        lazy=False,
        mesh_ifp=None,
        use_cuda=False,
    ):
        # logger.info('refine_mesh: ...')

        # https://github.com/cdcseacave/openMVS/blob/master/apps/RefineMesh/RefineMesh.cpp
        # https://github.com/cdcseacave/openMVS/wiki/Usage
        if (
            not os.path.isfile(os.path.join(openmvs_workspace_dp, openmvs_ofn))
            or not lazy
        ):
            refine_mesh_call = [
                self.refine_mesh_fp,
                "-i",
                openmvs_ifn,
                "-w",
                openmvs_workspace_dp,
                "-o",
                openmvs_ofn,
                "--use-cuda",
                str(int(use_cuda)),
            ]

            if mesh_ifp is not None:
                refine_mesh_call += ["--mesh-file", mesh_ifp]

            logger.info(str(refine_mesh_call))
            refine_mesh_proc = subprocess.Popen(refine_mesh_call)
            refine_mesh_proc.wait()

        # logger.info('refine_mesh: Done')

    def texture_mesh(
        self,
        openmvs_workspace_dp,
        openmvs_ifn,
        openmvs_ofn,
        export_type,
        lazy=False,
    ):
        # export_type: '.ply' or '.obj'
        logger.info("texture_mesh: ...")

        if not (export_type == "ply" or export_type == "obj"):
            logger.vinfo("export_type", export_type)
            assert False

        export_file = os.path.splitext(openmvs_ofn)[0] + "." + export_type

        if (
            not os.path.isfile(openmvs_ofn)
            or not os.path.isfile(export_file)
            or not lazy
        ):
            texture_mesh_call = [
                self.texture_mesh_fp,
                "-i",
                openmvs_ifn,
                "-w",
                openmvs_workspace_dp,
                "-o",
                openmvs_ofn,
                "--export-type",
                export_type,
            ]

            logger.info(str(texture_mesh_call))
            pRecons = subprocess.Popen(texture_mesh_call)
            pRecons.wait()
        logger.info("texture_mesh: Done")

    def perform_mvs(
        self,
        ifp,
        openmvs_workspace,
        openmvs_ofp,
        image_idp=None,  # For NVM input
        lazy=False,
    ):
        # ifp can be an .mvs (OpenMVS) or a .nvm (VisualSfM) or .bin/.json (OpenMVG) file
        # openmvs_ofp can be an .obj or an.ply file

        logger.info("perform_mvs : ...")
        logger.vinfo("openmvs_ofp", openmvs_ofp)

        if not os.path.isdir(openmvs_workspace):
            os.mkdir(openmvs_workspace)

        openmvs_workspace_temp = os.path.join(openmvs_workspace, "temp")
        if not os.path.isdir(openmvs_workspace_temp):
            os.mkdir(openmvs_workspace_temp)

        if os.path.splitext(ifp)[1] == ".mvs":
            logger.info("OpenMVS file detected")
            openmvs_ifp = ifp
        elif os.path.splitext(ifp)[1] == ".nvm":
            logger.info("NVM file detected")
            assert image_idp is not None
            openmvs_ifp = os.path.splitext(ifp)[0] + ".mvs"
            # TODO: This folder is only created if the parameters actually show
            #  a distortion coefficient. Otherwise the original image folder
            #  is referenced in the mvs file
            # undistorted_image_fp = os.path.join(
            #   os.path.dirname(openmvs_ifp), "undistorted_images/"
            # )
            self.convert_visualsfm_to_openMVS(
                nvm_ifp=ifp,
                image_idp=image_idp,
                openmvs_workspace_temp=openmvs_workspace_temp,
                openmvs_ofp=openmvs_ifp,
            )
        elif (
            os.path.splitext(ifp)[1] == ".bin"
            or os.path.splitext(ifp)[1] == ".json"
        ):
            logger.info("OpenMVG file detected")
            assert image_idp is not None
            openmvs_ifp = os.path.splitext(ifp)[0] + ".mvs"

            from ssr.sfm_utility.openmvg.openmvg_sfm import (
                OpenMVGReconstructor,
            )

            OpenMVGReconstructor.export_to_openmvs(ifp=ifp, ofp=openmvs_ifp)
        else:
            assert False

        dense_mvs_fn = "dense.mvs"
        dense_mvs_fp = os.path.join(openmvs_workspace, dense_mvs_fn)
        self.densify_point_cloud(
            openmvs_ifp, openmvs_workspace_temp, dense_mvs_fp, lazy
        )
        mesh_mvs_fn = "dense_mesh.mvs"
        mesh_mvs_fp = os.path.join(openmvs_workspace, mesh_mvs_fn)
        self.reconstruct_mesh(
            dense_mvs_fp, openmvs_workspace_temp, mesh_mvs_fp, lazy
        )
        texture_mvs_fn = "dense_mesh_texture.mvs"
        texture_mvs_fp = os.path.join(openmvs_workspace, texture_mvs_fn)
        export_type = "obj"
        self.texture_mesh(
            mesh_mvs_fp,
            openmvs_workspace_temp,
            texture_mvs_fp,
            export_type,
            lazy,
        )
        texture_ply_fp = (
            os.path.splitext(texture_mvs_fp)[0] + "." + export_type
        )

        shutil.copyfile(texture_ply_fp, openmvs_ofp)

        if export_type == "ply":
            shutil.copyfile(
                os.path.splitext(texture_ply_fp)[0] + ".png",
                os.path.splitext(openmvs_ofp)[0] + ".png",
            )
        elif export_type == "obj":
            shutil.copyfile(
                os.path.splitext(texture_ply_fp)[0] + ".mtl",
                os.path.splitext(openmvs_ofp)[0] + ".mtl",
            )
            shutil.copyfile(
                os.path.join(
                    os.path.dirname(texture_ply_fp),
                    "dense_mesh_texture_material_0_map_Kd.jpg",
                ),
                os.path.join(
                    os.path.dirname(openmvs_ofp),
                    "dense_mesh_texture_material_0_map_Kd.jpg",
                ),
            )

        logger.info("perform_mvs : Done")
