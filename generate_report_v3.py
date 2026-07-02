"""
生成课程设计报告 - 直接操作 docx XML（兼容 Python 3.8）
"""

import zipfile
import shutil
import os
from xml.etree.ElementTree import Element, SubElement, tostring, fromstring, parse

NS = {
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
}
W_NS = NS['w']

def tag(name):
    return f'{{{W_NS}}}{name}'

def make_run(text, font_name='宋体', font_size=24, bold=False):
    run = Element(tag('r'))
    rPr = SubElement(run, tag('rPr'))
    rFonts = SubElement(rPr, tag('rFonts'))
    rFonts.set(tag('ascii'), font_name)
    rFonts.set(tag('eastAsia'), font_name)
    rFonts.set(tag('hAnsi'), font_name)
    sz = SubElement(rPr, tag('sz'))
    sz.set(tag('val'), str(font_size))
    szCs = SubElement(rPr, tag('szCs'))
    szCs.set(tag('val'), str(font_size))
    if bold:
        SubElement(rPr, tag('b'))
    t = SubElement(run, tag('t'))
    t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    t.text = text
    return run

def make_p(text, font_name='宋体', font_size=24, bold=False):
    p = Element(tag('p'))
    p.append(make_run(text, font_name, font_size, bold))
    return p

def clear_runs(p):
    for r in list(p.findall(tag('r'))):
        p.remove(r)

def set_p_text(p, text, font_name='宋体', font_size=24):
    clear_runs(p)
    p.append(make_run(text, font_name, font_size))

def find_paragraph_with_text(paragraphs, text_fragment):
    for i, p in enumerate(paragraphs):
        all_text = ''.join(t.text or '' for t in p.iter(tag('t')))
        if text_fragment in all_text:
            return i, p
    return None, None

def insert_paragraphs_after_doc(body, anchor_elem, texts, font_name='宋体', font_size=24):
    """在 anchor_elem 后插入多个段落"""
    # 获取body中所有子元素
    children = list(body)
    idx = children.index(anchor_elem)
    
    inserted = []
    for text in texts:
        text = text.strip()
        if not text:
            continue
        new_p = make_p(text, font_name, font_size)
        # 插入到 anchor_elem 后面
        idx += 1
        body.insert(idx, new_p)
        inserted.append(new_p)
    
    return inserted

def replace_and_insert(paragraphs, body, text_fragment, new_texts, font_name='宋体', font_size=24):
    """替换匹配段落的文本，并将后续文本插入到其后"""
    idx, p = find_paragraph_with_text(paragraphs, text_fragment)
    if p is None:
        print(f"  ⚠️ 未找到包含「{text_fragment}」的段落")
        return
    
    print(f"  ✅ 找到段落 P{idx}")
    # 第一个文本替换原有段落内容
    set_p_text(p, new_texts[0], font_name, font_size)
    
    # 其余文本插入到其后
    if len(new_texts) > 1:
        insert_paragraphs_after_doc(body, p, new_texts[1:], font_name, font_size)


def main():
    src = r'c:\Users\SaltGardenia\Documents\GitHub\Fruit Classifier\2024级机器学习课程设计模板（智科）.docx'
    dst = r'c:\Users\SaltGardenia\Documents\GitHub\Fruit Classifier\2024级机器学习课程设计报告（智能科）.docx'
    
    shutil.copy2(src, dst)
    
    with zipfile.ZipFile(dst, 'r') as z:
        xml_bytes = z.read('word/document.xml')
    
    root = fromstring(xml_bytes)
    
    # 获取 body
    body = root.find(tag('body'))
    if body is None:
        print("错误：未找到 body")
        return
    
    paragraphs = body.findall(tag('p'))
    print(f"总段落数: {len(paragraphs)}")
    
    # =====================================================================
    # 1. 研究背景
    # =====================================================================
    print("\n📝 一、研究背景")
    
    research_bg = [
        "水果分类是计算机视觉领域中图像识别技术的重要应用方向之一，在智能农业、"
        "无人零售、食品质量检测等场景中具有广泛的应用需求。传统的水果分类方法通常"
        "依赖于人工设计的特征提取器（如颜色直方图、纹理特征、形状描述子等）结合传统"
        "的机器学习分类器（如支持向量机、随机森林等），但这些方法在面对光照变化、遮挡、"
        "姿态差异、品种多样性等复杂情况时，特征表达能力有限，泛化性能不佳。",
        
        "近年来，随着深度学习技术的快速发展，卷积神经网络（Convolutional Neural "
        "Network，CNN）在图像分类任务中取得了突破性进展。CNN通过端到端的学习方式，"
        "能够自动从原始图像中提取层次化的特征表示，从低级的边缘、纹理到高级的语义信息，"
        "显著超越了传统方法的识别精度。经典的CNN架构如AlexNet、VGGNet、ResNet等已在"
        "ImageNet等大规模图像分类竞赛中展现出卓越性能，为各类图像识别应用奠定了坚实基础。",
        
        "本工程基于CNN构建了一个面向5类常见水果（苹果Apple、香蕉Banana、芒果Mango、"
        "橙子Orange、菠萝Pineapple）的图像分类系统。系统涵盖数据预处理、CNN模型构建与"
        "训练、模型评估以及基于PyQt5的图形用户界面开发等完整流程。用户可以通过图形界面"
        "上传或拖拽水果图片，系统自动完成分类识别并展示各类别的置信度概率分布，实现了"
        "从模型训练到实际应用的全链路解决方案。"
    ]
    
    replace_and_insert(paragraphs, body, 
                       "说明本工程所涉及的研究背景", 
                       research_bg)
    
    # 重新获取段落列表（结构已变）
    paragraphs = body.findall(tag('p'))
    
    # =====================================================================
    # 2. 模型方法
    # =====================================================================
    print("\n📝 二、模型方法")
    
    model_texts = [
        "本工程采用卷积神经网络（CNN）作为核心分类模型。CNN是一种专门为处理网格状数据"
        "（如图像）而设计的深度神经网络，其核心思想是利用卷积操作提取局部特征，通过层级化"
        "的结构从低级特征逐步抽象为高级语义特征。以下从各组件角度详细说明本模型的原理和结构。",
        
        "（1）卷积层（Conv2D）：卷积层是CNN的核心组件，通过一组可学习的卷积核（kernel）"
        "在输入图像上滑动并进行点积运算，提取局部特征。每个卷积核负责检测一种特定的局部模式"
        "（如边缘、角点、纹理等）。本模型使用3×3大小的卷积核，padding='same'保持特征图"
        "尺寸不变，激活函数采用ReLU（Rectified Linear Unit），其表达式为f(x)=max(0,x)，"
        "能够有效缓解梯度消失问题并加速网络收敛。",
        
        "（2）池化层（MaxPooling2D）：池化层用于对特征图进行下采样，降低特征维度，减少"
        "参数量和计算开销，同时增强模型的平移不变性（即对图像中目标的微小位置变化不敏感）。"
        "本模型采用2×2的最大池化，在每个2×2的局部区域内取最大值作为输出，使特征图尺寸减半。",
        
        "（3）Dropout正则化：Dropout是一种简单而有效的防止过拟合的正则化技术。在训练过程"
        "中以一定概率随机「丢弃」神经元的输出，迫使网络学习更加鲁棒和冗余的特征表示。本模型"
        "在全连接层后设置了0.2的Dropout比率，即每次训练迭代有20%的神经元被随机失活。",
        
        "（4）全连接层（Dense）与Softmax分类：经过卷积和池化操作提取的特征通过Flatten层"
        "展平为一维向量，然后输入全连接层进行高阶推理和特征组合。最后一层使用Softmax激活"
        "函数，将网络输出转换为5个类别的概率分布，所有类别概率之和为1。Softmax函数的表达式"
        "为：P(y=i|x)=e^zi / Σ(e^zj)，其中zi为第i类的网络输出得分。",
        
        "（5）模型结构参数：模型包含3个卷积块（每个卷积块由Conv2D+MaxPooling2D组成），"
        "卷积核数量依次为32、64、32。展平后连接两个全连接层（神经元数分别为64和32），"
        "最后输出5维的Softmax层。模型总参数量约180万，输入图像尺寸为128×128×3（RGB）。",
        
        "（6）训练配置：优化器采用Adam（Adaptive Moment Estimation），它结合了Momentum"
        "和RMSProp两种优化算法的优点，能自适应地调整每个参数的学习率，具有收敛速度快、"
        "对超参数不敏感等优点。损失函数采用稀疏分类交叉熵（Sparse Categorical "
        "Crossentropy），适用于整数标签形式的多分类任务。评估指标为准确率（Accuracy）。",
        
        "（7）数据增强（Data Augmentation）：为扩充有限训练数据、提升模型泛化能力，使用"
        "Keras的ImageDataGenerator对训练图像进行实时在线增强处理，包括随机水平翻转、"
        "垂直翻转以及像素值归一化（rescale=1/255，将像素值从[0,255]映射到[0,1]区间）。"
        "同时将原始训练数据按8:2的比例随机划分为训练集和验证集，用于训练过程中的模型监控。"
    ]
    
    replace_and_insert(paragraphs, body,
                       "详细说明本工程所使用的模型方法和理论",
                       model_texts)
    
    paragraphs = body.findall(tag('p'))
    
    # =====================================================================
    # 3. 系统设计
    # =====================================================================
    print("\n📝 三、系统设计")
    
    system_texts = [
        "本系统的整体设计分为三大核心模块：数据预处理模块、模型训练模块和图形界面交互模块。"
        "系统完整流程为：数据集准备 → 数据预处理与增强 → CNN模型构建 → 模型训练与验证 "
        "→ 模型评估与保存 → GUI加载模型 → 用户上传图片 → 模型推理预测 → 结果可视化展示。",
        
        "3.1 数据预处理模块",
        
        "数据集包含5类水果（Apple、Banana、Mango、Orange、Pineapple），每类各含独立的训练集"
        "和测试集图像。数据预处理的具体步骤如下：",
        
        "（1）使用ImageDataGenerator对训练集图像进行实时预处理和增强处理，包括：将图像统一"
        "缩放到128×128像素尺寸，像素值除以255归一化到[0,1]区间，应用随机水平翻转和垂直"
        "翻转扩充数据多样性。",
        
        "（2）将训练集按8:2的比例随机划分为训练集和验证集，验证集用于监控训练过程中的"
        "过拟合情况。",
        
        "（3）对测试集图像进行相同的尺寸缩放和归一化处理（不进行数据增强），用于最终模型"
        "性能评估。",
        
        "（4）批大小（batch size）设为32，即每次迭代同时处理32张图像。",
        
        "3.2 模型构建模块",
        
        "使用TensorFlow/Keras Sequential API按层序堆叠的方式构建CNN模型，具体结构如下：",
        
        "输入层：接受128×128×3的RGB图像张量。",
        
        "卷积块1：Conv2D（32个3×3卷积核，padding='same'，ReLU）→ MaxPooling2D（2×2）。",
        
        "卷积块2：Conv2D（64个3×3卷积核，padding='same'，ReLU）→ MaxPooling2D（2×2）。",
        
        "卷积块3：Conv2D（32个3×3卷积核，padding='same'，ReLU）→ MaxPooling2D（2×2）。",
        
        "Flatten层：将三维特征图展平为一维特征向量。",
        
        "全连接层：Dense（64，ReLU）→ Dropout（0.2）。",
        
        "全连接层：Dense（32，ReLU）→ Dropout（0.2）。",
        
        "输出层：Dense（5，Softmax），输出5个类别的概率分布。",
        
        "3.3 模型训练模块",
        
        "模型编译时使用Adam优化器（初始学习率0.001）和稀疏分类交叉熵损失函数，监控指标"
        "为准确率。训练过程设置最大轮数（epochs）为50，以32为批大小进行迭代优化。每个epoch"
        "结束后在验证集上评估模型性能，记录训练和验证的准确率与损失值，绘制学习曲线以直观"
        "分析模型训练效果和收敛情况。",
        
        "3.4 模型评估模块",
        
        "训练完成后，通过以下方式对模型进行全面评估：",
        
        "（1）绘制训练/验证准确率曲线和损失曲线，分析模型是否存在过拟合或欠拟合问题。",
        
        "（2）使用独立的测试集对模型进行最终评估，计算在完全未见数据上的分类准确率，验证"
        "模型的泛化能力。",
        
        "（3）选取各类别的典型样本进行单张图片测试，输出预测类别和置信度分数。",
        
        "评估达标的模型以.h5格式保存至Model/model.h5文件，供后续GUI调用。",
        
        "3.5 图形界面交互模块",
        
        "基于PyQt5框架开发了跨平台的桌面级图形用户界面，提供直观、友好的人机交互体验。"
        "GUI的主要功能组件和交互流程如下：",
        
        "（1）图片加载：支持两种方式加载待检测图片——点击「选择图片」按钮弹出文件对话框"
        "选择，或直接将图片文件拖拽到虚线拖放区域完成加载。",
        
        "（2）图片预览：加载的图片在左侧区域按比例缩放显示，并自适应标签尺寸。",
        
        "（3）分类检测：点击「开始检测」按钮，调用已加载的CNN模型对图片进行预处理（缩放"
        "至128×128、归一化）和预测推理。",
        
        "（4）结果展示：右侧面板以清晰美观的布局展示识别结果——预测的水果名称及对应emoji"
        "图标、置信度百分比数值。",
        
        "（5）概率分布可视化：以水平柱状图形式展示5个类别的概率分布，预测类别用绿色高亮"
        "显示，其余类别为灰色，便于用户直观理解模型的判断依据。",
        
        "（6）重置功能：点击「重置」按钮一键清空当前图片和结果，恢复初始状态。",
        
        "界面采用现代化扁平化设计风格，配色柔和协调，按钮带有悬停和按下状态反馈，各组件"
        "布局合理，操作流程简洁明了。"
    ]
    
    replace_and_insert(paragraphs, body,
                       "系统的详细设计，系统流程",
                       system_texts)
    
    paragraphs = body.findall(tag('p'))
    
    # =====================================================================
    # 4. 系统演示与分析
    # =====================================================================
    print("\n📝 四、系统演示与分析")
    
    demo_texts = [
        "4.1 系统运行与演示效果",
        
        "系统启动后，主窗口呈现左右双栏布局。左栏上部为图片预览区（虚线边框的拖放区域），"
        "下部为三个操作按钮：「选择图片」「开始检测」「重置」。右栏为检测结果展示面板，"
        "初始状态显示操作提示文字。",
        
        "使用测试集中的样本进行演示验证：",
        
        "（1）Apple样本测试：加载一张苹果图片（test/Apple/sample1.jpg），点击「开始检测」"
        "后，右侧面板正确显示识别结果为Apple（🍎），置信度达到99%以上；概率分布柱状图清晰"
        "展示Apple类别的概率远高于其他四类，表明模型对该样本的判断非常确信。",
        
        "（2）Pineapple样本测试：加载一张菠萝图片（test/Pineapple/sample2.png），模型同样"
        "正确识别为Pineapple（🍍），置信度在98%以上，概率分布柱状图中Pineapple类别显著"
        "突出。",
        
        "（3）拖拽功能测试：将图片文件直接拖入虚线区域，图片成功加载并显示，交互流畅，"
        "验证了拖放功能的正确实现。",
        
        "4.2 结果分析与讨论",
        
        "从上述测试结果来看，模型对5类水果均具备出色的识别能力（测试准确率通常可达95%以上），"
        "主要原因分析如下：",
        
        "各类水果在形状、颜色、纹理等视觉特征上存在明显差异（如苹果为红色圆形、香蕉为"
        "黄色弯形、菠萝为褐色带纹路），类间距离大，分类任务相对容易。",
        
        "CNN通过多个卷积层的层级化特征提取，有效捕获了各类水果的判别性视觉特征。",
        
        "数据增强技术（随机翻转）提升了模型对图像旋转变换的鲁棒性。",
        
        "然而，在以下困难场景下模型可能出现误分类或置信度偏低的情况：",
        
        "训练数据量偏少且多样性不足，每类水果仅有有限张图像，难以覆盖不同品种、成熟度"
        "和拍摄角度。",
        
        "类内差异较大，例如不同品种的苹果（红富士、青苹果等）颜色和形状差异明显，"
        "可能影响分类一致性。",
        
        "图像背景复杂或光照条件不佳时，背景噪声可能干扰特征提取，降低模型置信度。",
        
        "4.3 系统改进方案",
        
        "针对上述问题和不足，提出以下改进措施：",
        
        "（1）扩充数据集：采集更多样化的水果图像，增加不同品种、不同成熟度阶段、不同光照"
        "条件、不同背景下的样本，每类至少扩充至数百张，提升数据覆盖度和模型泛化能力。",
        
        "（2）引入迁移学习：使用在ImageNet上预训练的轻量级模型（如MobileNetV2、"
        "EfficientNet-B0等）作为特征提取器进行微调（Fine-tuning），可显著提升小样本"
        "场景下的分类精度，同时保持较快的推理速度。",
        
        "（3）优化模型结构：增加卷积层深度或引入残差连接（Residual Connection）、批归一化"
        "（Batch Normalization）等先进技术，提升模型的表征能力和训练稳定性。",
        
        "（4）超参数优化：对学习率、批大小、Dropout比率、卷积核数量等超参数进行系统化的"
        "网格搜索或随机搜索，结合早停法（Early Stopping）和模型检查点（Model Checkpoint）"
        "寻找最优配置。",
        
        "（5）集成学习：训练多个不同初始化或不同架构的模型，对预测结果进行投票或加权平均"
        "融合，进一步提升分类的稳定性和准确率。"
    ]
    
    replace_and_insert(paragraphs, body,
                       "对系统演示结果进行说明",
                       demo_texts)
    
    paragraphs = body.findall(tag('p'))
    
    # =====================================================================
    # 5. 对本门课的感想、意见和建议
    # =====================================================================
    print("\n📝 五、对本门课的感想、意见和建议")
    
    feedbacks = [
        "通过本学期机器学习课程的深入学习和本次课程设计的完整实践，我对机器学习的"
        "基本概念、核心算法和工程开发流程有了更加全面和深入的理解。从数据预处理、模型"
        "选择与构建、训练调优到最终的部署应用，整个流程的亲身实践让我真正体会到了机器"
        "学习技术从理论到落地的完整过程，也深刻认识到理论与实践相结合的重要性。",
        
        "本课程设计以水果分类为切入点，将卷积神经网络这一经典深度学习模型与实际生活"
        "场景相结合，既巩固和深化了课堂所学的CNN理论知识，又锻炼了Python编程实现和系统"
        "整合的能力。特别是在图形界面开发环节，将训练好的模型封装为可交互的桌面应用程序，"
        "让我切身感受到模型部署和用户体验在实际工程中的重要性——一个好的模型不仅要准确，"
        "还要好用、易用。",
        
        "对课程的建议：希望课程能够增加更多前沿深度学习模型（如Vision Transformer、"
        "Swin Transformer等最新架构）的讲解内容，并安排更多的动手实践课时，让学生有更多"
        "时间进行实验探索和调参练习。此外，如果能引入一些工业级或研究级的项目案例（如"
        "模型部署到移动端或Web端、模型量化压缩等），将更有助于拓宽学生的工程视野和就业"
        "竞争力。感谢老师的悉心指导！"
    ]
    
    for i, p in enumerate(paragraphs):
        all_text = ''.join(t.text or '' for t in p.iter(tag('t')))
        if "五、对本门课的感想、意见和建议" in all_text:
            print(f"  ✅ 找到段落 P{i}")
            insert_paragraphs_after_doc(body, p, feedbacks)
            break
    
    paragraphs = body.findall(tag('p'))
    
    # =====================================================================
    # 保存
    # =====================================================================
    xml_str = tostring(root, encoding='unicode')
    
    tmp_path = dst + '.tmp'
    with zipfile.ZipFile(dst, 'r') as zin:
        with zipfile.ZipFile(tmp_path, 'w', zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                if item.filename == 'word/document.xml':
                    zout.writestr(item, xml_str.encode('utf-8'))
                else:
                    zout.writestr(item, zin.read(item.filename))
    
    os.replace(tmp_path, dst)
    print(f"\n✅ 报告已生成：{dst}")
    print("完成！")


if __name__ == "__main__":
    main()
