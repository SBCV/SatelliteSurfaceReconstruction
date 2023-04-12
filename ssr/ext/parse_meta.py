#  ===============================================================================================================
#  Copyright (c) 2019, Cornell University. All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without modification, are permitted provided that
#  the following conditions are met:
#
#      * Redistributions of source code must retain the above copyright otice, this list of conditions and
#        the following disclaimer.
#
#      * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and
#        the following disclaimer in the documentation and/or other materials provided with the distribution.
#
#      * Neither the name of Cornell University nor the names of its contributors may be used to endorse or
#        promote products derived from this software without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED
#  WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#  A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDERS OR CONTRIBUTORS BE LIABLE
#  FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
#  TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
#  HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
#   NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY
#  OF SUCH DAMAGE.
#
#  Author: Kai Zhang (kz298@cornell.edu)
#
#  The research is based upon work supported by the Office of the Director of National Intelligence (ODNI),
#  Intelligence Advanced Research Projects Activity (IARPA), via DOI/IBC Contract Number D17PC00287.
#  The U.S. Government is authorized to reproduce and distribute copies of this work for Governmental purposes.
#  ===============================================================================================================


from xml.etree.ElementTree import ElementTree
import dateutil.parser


def parse_meta(xml_file):
    rpc_dict = {}

    tree = ElementTree()
    tree.parse(xml_file)

    b = tree.find("IMD/IMAGE/SATID")  # WorldView

    if b.text not in ["WV01", "WV02", "WV03"]:
        raise ValueError("not a WorldView satellite!")

    im = tree.find("RPB/IMAGE")
    l = im.find("LINENUMCOEFList/LINENUMCOEF")
    rpc_dict["rowNum"] = [float(c) for c in l.text.split()]
    l = im.find("LINEDENCOEFList/LINEDENCOEF")
    rpc_dict["rowDen"] = [float(c) for c in l.text.split()]
    l = im.find("SAMPNUMCOEFList/SAMPNUMCOEF")
    rpc_dict["colNum"] = [float(c) for c in l.text.split()]
    l = im.find("SAMPDENCOEFList/SAMPDENCOEF")
    rpc_dict["colDen"] = [float(c) for c in l.text.split()]

    # self.inverseBias = float(im.find('ERRBIAS').text)

    # scale and offset
    rpc_dict["rowOff"] = float(im.find("LINEOFFSET").text)
    rpc_dict["rowScale"] = float(im.find("LINESCALE").text)

    rpc_dict["colOff"] = float(im.find("SAMPOFFSET").text)
    rpc_dict["colScale"] = float(im.find("SAMPSCALE").text)

    rpc_dict["latOff"] = float(im.find("LATOFFSET").text)
    rpc_dict["latScale"] = float(im.find("LATSCALE").text)

    rpc_dict["lonOff"] = float(im.find("LONGOFFSET").text)
    rpc_dict["lonScale"] = float(im.find("LONGSCALE").text)

    rpc_dict["altOff"] = float(im.find("HEIGHTOFFSET").text)
    rpc_dict["altScale"] = float(im.find("HEIGHTSCALE").text)

    # meta dict
    meta_dict = {"rpc": rpc_dict}

    # image dimensions
    meta_dict["height"] = int(tree.find("IMD/NUMROWS").text)
    meta_dict["width"] = int(tree.find("IMD/NUMCOLUMNS").text)

    # date string is in ISO format
    meta_dict["capTime"] = dateutil.parser.parse(
        tree.find("IMD/IMAGE/TLCTIME").text
    )

    # sun direction
    meta_dict["sunAzim"] = float(tree.find("IMD/IMAGE/MEANSUNAZ").text)
    meta_dict["sunElev"] = float(tree.find("IMD/IMAGE/MEANSUNEL").text)

    # satellite direction
    meta_dict["satAzim"] = float(tree.find("IMD/IMAGE/MEANSATAZ").text)
    meta_dict["satElev"] = float(tree.find("IMD/IMAGE/MEANSATEL").text)

    # cloudless or not
    meta_dict["cloudCover"] = float(tree.find("IMD/IMAGE/CLOUDCOVER").text)

    meta_dict["sensor_id"] = tree.find("IMD/IMAGE/SATID").text

    return meta_dict
