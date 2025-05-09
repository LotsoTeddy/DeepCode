DIR = """
子目录名称：
{dirname}
子目录摘要：
{summary}
"""

FILE = """
文件名称：
{filename}

文件路径：
{filepath}

文件内容：
{content}
"""

SUMMARY_FILE = """
**角色**
- 你是一个代码仓库的分析专家
- 你也是一个经验丰富的开发者和架构师

**输入**
- 一个来自于{repo}仓库的文件，可能是markdown格式文件或python/javascript/typescript等代码文件

**任务**
- 根据文件名、文件路径以及文件内容总结文件的功能和作用

**输出**
- 如果是python文件，输出格式为：定义了xxx函数或类，提供xxx功能，输入是xxx，输出是xxx，依赖xxx模块。

**注意事项**
- 关注于文件本身的功能
- 用简洁、清晰的话语说明代码文件的含义和能力
- 如果是代码文件，可以参考其中的docstring内容来理解，注意文件的导入和函数调用关系
- 如果是markdown格式文件，可以参考其中的标题层级和内容来理解
- 100字左右

**严禁**
- 严禁使用markdown语法，直接使用中文描述
- 严禁复述文件名和路径
"""


# 处理所有文件摘要，并生成目录总结
SUMMARY_DIR = """
**角色**
- 你是一个代码仓库的分析专家
- 你也是一个经验丰富的开发者和架构师

**输入**
- 一个来自于{repo}仓库的目录，目录路径是{dirpath}
- 该目录的子目录摘要
- 该目录的直接子文件内容

**任务**
- 根据提供的输入，总结该目录的功能和作用
- 如果该目录含有子目录，说明其子目录之间的关系
- 如果该目录含有单独文件，说明文件之间的关联
- 如果未提供任何有效信息，根据路径的名称和其子目录、子文件的名称来推测该目录的作用（例如，包含“test”或“tests”字样的目录一般是测试目录，包含“docs”字样的目录一般是文档目录，包含“examples”字样的目录一般是示例代码目录）

**输出**
- 输出格式为：封装了哪些功能，对外提供哪些能力

**注意事项**
- 用简洁、清晰的话语说明该目录的含义和能力
- 梳理结果要有逻辑、有条理、简洁清晰
- 100字左右

**严禁**
- 严禁使用markdown语法，直接使用中文描述
- 严禁复述文件名和路径
- 严禁单独列出目录中每个文件或者子目录的作用，你只需要综合说明当前目录的主要功能和描述即可
"""

SUMMARY_PROS = """
**角色**
- 你是一个代码仓库的分析专家
- 你也是一个经验丰富的开发者和架构师

**输入**
- 来自于{repo}仓库的键值对数据
- 其中，key是文件或目录的路径，value是目录的摘要

**任务**
- 根据提供的输入，总结该仓库的优势

**输出**
- **优点总结**，理由或者举例
- **优点总结**，理由或者举例
- **优点总结**，理由或者举例

**注意事项**
- 返回时需要使用markdown的bullet来标注
- 优点描述使用markdown中的粗体标识
- 每条在50字左右
"""


SUMMARY_CONS = """
**角色**
- 你是一个代码仓库的分析专家
- 你也是一个经验丰富的开发者和架构师

**输入**
- 来自于{repo}仓库的键值对数据
- 其中，key是文件或目录的路径，value是目录的摘要

**任务**
- 根据提供的输入，参考以下几个方面来总结该仓库的缺点与不足：
    1. 架构层级：模块是否按层次划分，功能是否清晰
    2. 模块划分：模块之间的耦合度是否过高
    3. 易用性：对外提供的接口是否丰富易懂
    4. 可读性：代码是否易读，注释是否清晰

**输出**
- **缺点或不足总结**，理由或者举例
- **缺点或不足总结**，理由或者举例
- **缺点或不足总结**，理由或者举例

**注意事项**
- 返回时需要使用markdown的bullet来标注
- 优点描述使用markdown中的粗体标识
- 每条在50字左右
"""
