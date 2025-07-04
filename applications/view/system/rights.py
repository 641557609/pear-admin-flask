import copy
from collections import OrderedDict

from flask import jsonify, current_app, Blueprint, render_template
from flask_login import login_required, current_user

from ...common.utils.http import table_api
from ...models import Power
from ...schemas import PowerOutSchema

bp = Blueprint('rights', __name__, url_prefix='/rights')


# 渲染配置
@bp.get('/configs')
@login_required
def configs():
    # 网站配置
    config = dict(logo={
        # 网站名称
        "title": current_app.config.get("SYSTEM_NAME"),
        # 网站图标
        "image": "/static/system/admin/images/logo.png"
        # 菜单配置
    }, menu={
        # 菜单数据来源
        "data": "/system/rights/menu",
        "collaspe": False,
        # 是否同时只打开一个菜单目录
        "accordion": True,
        "method": "GET",
        # 是否开启多系统菜单模式
        "control": False,
        # 顶部菜单宽度 PX
        "controlWidth": 500,
        # 默认选中的菜单项
        "select": "0",
        # 是否开启异步菜单，false 时 data 属性设置为菜单数据，false 时为 json 文件或后端接口
        "async": True
    }, tab={
        # 是否开启多选项卡
        "enable": True,
        # 切换选项卡时，是否刷新页面状态
        "keepState": True,
        # 是否开启 Tab 记忆
        "session": True,
        # 预加载
        "preload": False,
        # 最大可打开的选项卡数量
        "max": 30,
        "index": {
            # 标识 ID , 建议与菜单项中的 ID 一致
            "id": "10",
            # 页面地址
            "href": "/system/rights/welcome",
            # 标题
            "title": "首页"
        }
    }, theme={
        # 默认主题色，对应 colors 配置中的 ID 标识
        "defaultColor": "2",
        # 默认的菜单主题 dark-theme 黑 / light-theme 白
        "defaultMenu": "dark-theme",
        # 是否允许用户切换主题，false 时关闭自定义主题面板
        "allowCustom": True
    }, colors=[{
        "id": "1",
        "color": "#2d8cf0"
    },
        {
            "id": "2",
            "color": "#5FB878"
        },
        {
            "id": "3",
            "color": "#1E9FFF"
        }, {
            "id": "4",
            "color": "#FFB800"
        }, {
            "id": "5",
            "color": "darkgray"
        }
    ], links=current_app.config.get("SYSTEM_PANEL_LINKS"), other={
        # 主页动画时长
        "keepLoad": 0,
        # 布局顶部主题
        "autoHead": False
    }, header={
        'message': '/system/rights/message'
    })
    return jsonify(config)


# 消息
@bp.get('/message')
@login_required
def message():
    return dict(code=200,
                data=[
                    {
                        "id": 1,
                        "title": "通知",
                        "children": [
                            {
                                "id": 11,
                                "avatar": "https://gw.alipayobjects.com/zos/rmsportal/ThXAXghbEsBCCSDihZxY.png",
                                "title": "你收到了 14 份新周报",
                                "context": "这是消息内容。",
                                "form": "就眠仪式",
                                "time": "刚刚"
                            },
                            {
                                "id": 12,
                                "avatar": "https://gw.alipayobjects.com/zos/rmsportal/OKJXDXrmkNshAMvwtvhu.png",
                                "title": "曲妮妮 已通过第三轮面试",
                                "context": "这是消息内容。",
                                "form": "就眠仪式",
                                "time": "刚刚"
                            },
                            {
                                "id": 11,
                                "avatar": "https://gw.alipayobjects.com/zos/rmsportal/kISTdvpyTAhtGxpovNWd.png",
                                "title": "可以区分多种通知类型",
                                "context": "这是消息内容。",
                                "form": "就眠仪式",
                                "time": "刚刚"
                            },
                            {
                                "id": 12,
                                "avatar": "https://gw.alipayobjects.com/zos/rmsportal/GvqBnKhFgObvnSGkDsje.png",
                                "title": "左侧图标用于区分不同的类型",
                                "context": "这是消息内容。",
                                "form": "就眠仪式",
                                "time": "刚刚"
                            },
                            {
                                "id": 11,
                                "avatar": "https://gw.alipayobjects.com/zos/rmsportal/ThXAXghbEsBCCSDihZxY.png",
                                "title": "内容不要超过两行字",
                                "context": "这是消息内容。",
                                "form": "就眠仪式",
                                "time": "刚刚"
                            }
                        ]
                    },
                    {
                        "id": 2,
                        "title": "消息",
                        "children": [
                            {
                                "id": 11,
                                "avatar": "https://gw.alipayobjects.com/zos/rmsportal/ThXAXghbEsBCCSDihZxY.png",
                                "title": "你收到了 14 份新周报",
                                "context": "这是消息内容。",
                                "form": "就眠仪式",
                                "time": "刚刚"
                            },
                            {
                                "id": 12,
                                "avatar": "https://gw.alipayobjects.com/zos/rmsportal/OKJXDXrmkNshAMvwtvhu.png",
                                "title": "曲妮妮 已通过第三轮面试",
                                "context": "这是消息内容。",
                                "form": "就眠仪式",
                                "time": "刚刚"
                            },
                            {
                                "id": 11,
                                "avatar": "https://gw.alipayobjects.com/zos/rmsportal/kISTdvpyTAhtGxpovNWd.png",
                                "title": "可以区分多种通知类型",
                                "context": "这是消息内容。",
                                "form": "就眠仪式",
                                "time": "刚刚"
                            },
                            {
                                "id": 12,
                                "avatar": "https://gw.alipayobjects.com/zos/rmsportal/GvqBnKhFgObvnSGkDsje.png",
                                "title": "左侧图标用于区分不同的类型",
                                "context": "这是消息内容。",
                                "form": "就眠仪式",
                                "time": "刚刚"
                            },
                            {
                                "id": 11,
                                "avatar": "https://gw.alipayobjects.com/zos/rmsportal/ThXAXghbEsBCCSDihZxY.png",
                                "title": "内容不要超过两行字",
                                "context": "这是消息内容。",
                                "form": "就眠仪式",
                                "time": "刚刚"
                            }
                        ]
                    },
                    {
                        "id": 3,
                        "title": "代办",
                        "children": []
                    }
                ])


# 菜单
@bp.get('/menu')
@login_required
def menu():
    if current_user.username != current_app.config.get("SUPERADMIN"):
        role = current_user.role
        powers = []
        for i in role:
            # 如果角色没有被启用就直接跳过
            if i.enable == 0:
                continue
            # 变量角色用户的权限
            for p in i.power:
                # 如果权限关闭了就直接跳过
                if p.enable == 0:
                    continue
                # 一二级菜单
                if int(p.type) in [0, 1] and p not in powers:
                    powers.append(p)

        power_schema = PowerOutSchema(many=True)  # 用已继承 ma.ModelSchema 类的自定制类生成序列化类
        power_dict = power_schema.dump(powers)  # 生成可序列化对象
        power_dict.sort(key=lambda x: (x['parent_id'], x['id']), reverse=True)

        menu_dict = OrderedDict()
        for _dict in power_dict:
            if _dict['id'] in menu_dict:
                # 当前节点添加子节点
                _dict['children'] = copy.deepcopy(menu_dict[_dict['id']])
                _dict['children'].sort(key=lambda item: item['sort'])
                # 删除子节点
                del menu_dict[_dict['id']]

            if _dict['parent_id'] not in menu_dict:
                menu_dict[_dict['parent_id']] = [_dict]
            else:
                menu_dict[_dict['parent_id']].append(_dict)
        return jsonify(sorted(menu_dict.get(0), key=lambda item: item['sort']))
    else:
        powers = Power.query.all()
        power_schema = PowerOutSchema(many=True)  # 用已继承 ma.ModelSchema 类的自定制类生成序列化类
        power_dict = power_schema.dump(powers)  # 生成可序列化对象
        power_dict.sort(key=lambda x: (x['parent_id'], x['id']), reverse=True)

        menu_dict = OrderedDict()
        for _dict in power_dict:
            if _dict['id'] in menu_dict:
                # 当前节点添加子节点
                _dict['children'] = copy.deepcopy(menu_dict[_dict['id']])
                _dict['children'].sort(key=lambda item: item['sort'])
                # 删除子节点
                del menu_dict[_dict['id']]

            if _dict['parent_id'] not in menu_dict:
                menu_dict[_dict['parent_id']] = [_dict]
            else:
                menu_dict[_dict['parent_id']].append(_dict)
        return jsonify(sorted(menu_dict.get(0), key=lambda item: item['sort']))


# 控制台页面
@bp.get('/welcome')
@login_required
def welcome():
    return render_template('system/analysis/main.html')
