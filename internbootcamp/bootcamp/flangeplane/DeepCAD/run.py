import os

from Edit_plain.parameter_editor import main

import json
import numpy as np

from itertools import islice
from tqdm import tqdm
from datetime import datetime
import subprocess

import multiprocessing
from joblib import Parallel, delayed


def para(data):
    # thickness < D
    # 0.4 * D < B1 < D
    # B1 + 2L < BoltCenterRadius < D - 2L
    # 5 < L < min(BoltCenterRadius - B1, D - BoltCenterRadius, 2**(-1/2) * BoltCenterRadius)
    # 4 <= bolt_count_edit < pi / (arcsin(L / BoltCenterRadius))
    # bolt_count_edit = bolt_count_edit // 2 * 2
    params_to_show = {
        "profiles": {
                        "D": data['ground_truth']['D'],                                 # 外半径
                        "B1": data['ground_truth']['B1'],                               # 内半径
                        "L": data['ground_truth']['L'],                                 # 螺栓孔半径
                        "BoltCenterRadius": data['ground_truth']['BoltCenterRadius']    # 螺栓孔中心所在圆的半径
                    }, 
        "extent": {"thickness": data['ground_truth']['thickness']},                     # 法兰厚度
        "others": {"bolt_count_edit": data['ground_truth']['bolt_count_edit']}}         # 螺栓孔数目
    material = {                                   
        "Name": data['ground_truth']['Name'],                                           # 材料名称
        "YoungsModulus": "{} MPa".format(data['ground_truth']['YoungsModulus']),        # 杨氏模量（弹性变形刚度）
        "PoissonRatio": str(data['ground_truth']['PoissonRatio']),                      # 泊松比（横向收缩比例）
        "Density": "{} kg/m^3".format(data['ground_truth']['Density'])                  # 密度
    }
    # 默认外径圆柱面固定，向内径圆柱面施加压强
    pressure = data['ground_truth']['pressure']  # 单位：MPa                                         

    # 添加新的路径定义
    param_values = [f"material-{material['Name'].replace(' ', '')}", f"pressure-{pressure}"]
    for param_type in params_to_show:
        for param_name in params_to_show[param_type]:
            value = params_to_show[param_type][param_name]
            param_values.append(f"{param_name}-{value}")
    dirname = "_".join(param_values)
    work_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'work_dir', pick, dirname)
    return params_to_show, material, pressure, work_dir


def process_line(line):
    data = json.loads(line)
    params_to_show, material, pressure, work_dir = para(data)
    os.makedirs(work_dir, exist_ok=True)
    '''
    if os.path.basename(work_dir) != "material-StainlessSteel304_pressure-40.65916207275845_D-304.2600743341063_B1-271.49122645674026_L-5.31126500078843_BoltCenterRadius-287.46828935527856_thickness-10.033397382513565_bolt_count_edit-170":
        return 
    '''
    if not os.path.exists(os.path.join(work_dir, "data.json")):
        try:
            main(params_to_show, material, pressure, work_dir)
        except Exception as e:
            print(e)


root_path = "/cpfs04/user/dengshujian/code/internbootcamp/examples/bootcamp_generator_outputs"
timestamp = "2025-08-18-14:48:28"
pick = "test"  # "train", "test"

lines = []
with open(os.path.join(root_path, timestamp, pick, "flangeplane.jsonl"), 'r', encoding='utf-8') as f:
    for line in f:
        lines.append(line.strip())

if 0:  # process
    num_cores = multiprocessing.cpu_count()
    Parallel(n_jobs=num_cores)(delayed(process_line)(line) for line in lines[: 50000])
else:  # write
    missed = []
    with open(os.path.join(root_path, timestamp, pick, "flangeplane_gt.jsonl"), 'w', encoding='utf-8') as fs:
        for line in tqdm(lines):
            data = json.loads(line)

            params_to_show, material, pressure, work_dir = para(data)
            dirname = os.path.basename(work_dir)
            # '''
            if dirname in [
                "material-GrayCastIron_pressure-44.696536899523565_D-157.94432554112325_B1-117.5679431141073_L-5.850023101219235_BoltCenterRadius-145.30576019966662_thickness-10.799608770835523_bolt_count_edit-78",
                "material-StainlessSteel304_pressure-40.65916207275845_D-304.2600743341063_B1-271.49122645674026_L-5.31126500078843_BoltCenterRadius-287.46828935527856_thickness-10.033397382513565_bolt_count_edit-170",
                "material-LowTemperatureCarbonSteel_pressure-70.43486795592949_D-93.89637291090528_B1-70.67041331312159_L-5.003273442010336_BoltCenterRadius-80.70125243952974_thickness-24.20979862782056_bolt_count_edit-46",
                "material-GrayCastIron_pressure-29.748443396987454_D-275.571345151945_B1-226.45325580408672_L-8.839786937627302_BoltCenterRadius-245.1963318650784_thickness-31.284399374664602_bolt_count_edit-36",
                "material-Chrome-MolyAlloySteel_pressure-97.52852650271426_D-368.9852672058928_B1-223.4343890259703_L-25.45045282474565_BoltCenterRadius-281.6933248456026_thickness-5.139311269572349_bolt_count_edit-28",
                "material-CarbonSteel-ASTMA105_pressure-51.06555441867917_D-127.363075972463_B1-61.19079535261694_L-10.263240618654343_BoltCenterRadius-85.15926733604795_thickness-43.06986709038378_bolt_count_edit-26",
                "material-StainlessSteel304_pressure-86.8499643441709_D-105.60801174409713_B1-54.83535981322092_L-7.247444957142967_BoltCenterRadius-84.23957828482429_thickness-22.854445793001016_bolt_count_edit-32",
                "material-Chrome-MolyAlloySteel_pressure-56.50516863505578_D-225.41940302676184_B1-145.80675996619965_L-7.672866024974075_BoltCenterRadius-162.03065792840485_thickness-22.453896167905963_bolt_count_edit-14",
                "material-StainlessSteel304_pressure-58.6154932470235_D-359.1105659016526_B1-195.92844195319782_L-32.12146356100088_BoltCenterRadius-265.50882144954414_thickness-34.40424978588183_bolt_count_edit-22",
                "material-GrayCastIron_pressure-82.02199274350717_D-379.2648068016008_B1-274.4516905898068_L-18.750611940961914_BoltCenterRadius-321.16886980230265_thickness-27.54290162963985_bolt_count_edit-40",
                "material-LowTemperatureCarbonSteel_pressure-44.17734205104571_D-376.76901203683667_B1-205.44525676440662_L-14.049066944219794_BoltCenterRadius-313.0679711794054_thickness-19.057520575983098_bolt_count_edit-12",
                "material-LowTemperatureCarbonSteel_pressure-59.867221561435805_D-51.97774389903438_B1-26.66242398495338_L-5.470297003229045_BoltCenterRadius-38.46892635598247_thickness-17.891680006858124_bolt_count_edit-22",
                "material-GrayCastIron_pressure-40.70171951474104_D-381.48549691091955_B1-300.2102286242698_L-13.984327767280668_BoltCenterRadius-329.5125822522565_thickness-29.12288764384912_bolt_count_edit-74",
                "material-CarbonSteel-ASTMA105_pressure-64.53456000686236_D-195.17290903140793_B1-86.58113388127538_L-8.939329522156072_BoltCenterRadius-125.7881292629364_thickness-31.83141528635541_bolt_count_edit-16",
                "material-StainlessSteel304_pressure-1.0997897831910524_D-261.712786354428_B1-241.25191411729162_L-5.000052718939611_BoltCenterRadius-251.71236311964967_thickness-27.542837183091955_bolt_count_edit-158",
                "material-StainlessSteel304_pressure-95.98388136322953_D-192.5764183601385_B1-155.1905921424923_L-6.481333959073769_BoltCenterRadius-177.98107191566484_thickness-42.228427356073055_bolt_count_edit-58",
                "material-Chrome-MolyAlloySteel_pressure-19.856123906130442_D-41.815250084468396_B1-18.90802173946582_L-5.054132957617947_BoltCenterRadius-29.109505657745306_thickness-20.440162596145957_bolt_count_edit-18",
                "material-GrayCastIron_pressure-31.10262633827154_D-132.89074205683244_B1-104.20295186805288_L-5.061134420997083_BoltCenterRadius-122.47797727344232_thickness-34.322044016165584_bolt_count_edit-76",
                "material-LowTemperatureCarbonSteel_pressure-65.56410646455414_D-217.5436952822591_B1-90.38291205423448_L-10.55358204720352_BoltCenterRadius-194.96019673469962_thickness-15.368181075546952_bolt_count_edit-58",
                "material-GrayCastIron_pressure-71.43952642425036_D-112.19852771615305_B1-82.08282765163327_L-5.6452702604244696_BoltCenterRadius-100.68246349384837_thickness-31.92787792643947_bolt_count_edit-56",
                "material-GrayCastIron_pressure-16.688799851712275_D-208.7555824645213_B1-156.93558406160756_L-9.82540728547825_BoltCenterRadius-179.3477829066785_thickness-38.19753592428211_bolt_count_edit-10",
                "material-Chrome-MolyAlloySteel_pressure-64.66584873062948_D-228.98634087249562_B1-122.09466242893137_L-8.621465664961521_BoltCenterRadius-201.67740317663333_thickness-11.081959194551644_bolt_count_edit-30",
                "material-Chrome-MolyAlloySteel_pressure-87.63463203826305_D-187.3934764411336_B1-78.91434250735831_L-17.372544748298623_BoltCenterRadius-142.12540756382458_thickness-44.57851670179087_bolt_count_edit-24",
                "material-CarbonSteel-ASTMA105_pressure-52.43033546877455_D-364.4183840956378_B1-334.5235814530012_L-5.490372578182895_BoltCenterRadius-350.3007320089582_thickness-43.41706343890191_bolt_count_edit-66",
                "material-GrayCastIron_pressure-69.4256461633479_D-107.66983067585349_B1-71.07874714240867_L-6.054830244419951_BoltCenterRadius-91.2460479862714_thickness-29.99293194544997_bolt_count_edit-18",
                "material-Chrome-MolyAlloySteel_pressure-93.31952490773504_D-212.27667440952598_B1-167.09035367220395_L-6.340948143979196_BoltCenterRadius-184.9006007358451_thickness-25.872481190254355_bolt_count_edit-66",
                "material-CarbonSteel-ASTMA105_pressure-43.15515081323029_D-227.1605262926645_B1-186.39197625398646_L-7.611281548609444_BoltCenterRadius-209.88107798834452_thickness-12.69544562310772_bolt_count_edit-28",
                "material-CarbonSteel-ASTMA105_pressure-52.65882946459141_D-154.889044979362_B1-86.91924863139839_L-7.196592298131098_BoltCenterRadius-128.80257080966504_thickness-14.04472680921069_bolt_count_edit-38",
                "material-GrayCastIron_pressure-16.58247505582542_D-158.57409203727147_B1-90.84728927070572_L-5.175509170340776_BoltCenterRadius-102.19122923210972_thickness-41.615837409568954_bolt_count_edit-62",
                "material-StainlessSteel304_pressure-22.276359073609665_D-83.6420324971719_B1-56.052059503717885_L-5.130125769049482_BoltCenterRadius-66.36651566239432_thickness-41.613237094874016_bolt_count_edit-22",
                "material-CarbonSteel-ASTMA105_pressure-58.592928140966414_D-183.01415529810123_B1-80.48429786696911_L-13.632716635888531_BoltCenterRadius-135.37896398641033_thickness-14.663902333824916_bolt_count_edit-16",
                "material-LowTemperatureCarbonSteel_pressure-15.304773481366668_D-176.0631347630934_B1-84.94435001409187_L-5.8589568631758375_BoltCenterRadius-135.27850988693342_thickness-34.278344319581585_bolt_count_edit-70",
                "material-GrayCastIron_pressure-70.90862989316591_D-233.88089605003213_B1-163.61732294689835_L-5.118986998292718_BoltCenterRadius-218.16719504677764_thickness-33.54759824841957_bolt_count_edit-8",
                "material-LowTemperatureCarbonSteel_pressure-93.81219134901137_D-136.4719555767423_B1-99.3040719437393_L-5.962402472332123_BoltCenterRadius-118.18626161297884_thickness-20.424496221422487_bolt_count_edit-32",
                "material-GrayCastIron_pressure-83.17691998916264_D-358.78319859087134_B1-195.1050171149553_L-8.793463045825261_BoltCenterRadius-335.28567193675866_thickness-33.094324006337416_bolt_count_edit-8",
                "material-GrayCastIron_pressure-65.29918840874818_D-79.46551597419268_B1-43.52482317965345_L-5.322438764268443_BoltCenterRadius-66.87247351919913_thickness-35.584921621195214_bolt_count_edit-36",
                "material-GrayCastIron_pressure-46.45156420478594_D-357.06056559646214_B1-276.2869307952631_L-5.843947330013269_BoltCenterRadius-293.9789681076073_thickness-10.06933408014656_bolt_count_edit-158",
                "material-Chrome-MolyAlloySteel_pressure-18.431054518178943_D-202.90572099630054_B1-101.23884885141437_L-22.641130191850312_BoltCenterRadius-148.37937992073034_thickness-7.805217274616831_bolt_count_edit-14",
                "material-GrayCastIron_pressure-13.600575428112313_D-315.4212452050738_B1-126.96448909985162_L-42.38309632301504_BoltCenterRadius-221.82653442532282_thickness-12.07120313535345_bolt_count_edit-14"
            ]:
                continue
            # '''
            try:
                with open(os.path.join(work_dir, "data.json"), "r") as f:
                    info = json.load(f)
                
                # postprocess
                disps = []
                for id in info["DISP"]:
                    disps.append(info["DISP"][id])
                disp = np.sqrt(np.sum(np.array(disps)**2, axis=1))
                disp_min = disp.min().item() * 1e6  # m -> μm
                disp_max = disp.max().item() * 1e6  # m -> μm

                data['ground_truth']['disp_min'] = disp_min + (disp_max - disp_min) / 4 * 3
                data['ground_truth']['disp_max'] = disp_min + (disp_max - disp_min) / 4 * 5

                fs.write(json.dumps(data, ensure_ascii=False) + '\n')
            except Exception as e:
                print(e)
                missed.append(dirname)
    for m in missed:
        print(m)
    print(len(missed))
        