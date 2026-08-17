from pathlib import Path
import re

# ============================================================
# 调整图片透明度.py
#
# 新结构：
# - 只修改当前目录中的 my.css
# - 其他背景 CSS 只保存 background-image，不再修改
#
# 不生成 .bak，请自行提前备份。
# ============================================================

MY_CSS = "my.css"

# ============================================================
# 透明度预设
#
# 数值越大：
#   黑色背景 / 遮罩越重，背景图片越不明显
#
# 数值越小：
#   UI 越透明，背景图片越明显
#
# startup:
#   body.in-progress::after 的启动阶段遮罩
#   建议与 workspace 接近，使启动前后视觉差异更小
# ============================================================

PRESETS = {
    "1": {
        "name": "较亮图片",
        "description": "图片较亮，黑色背景较重，优先保证文字可读性",
        "workspace": 0.90,
        "modal": 0.84,
        "modal_alt": 0.78,
        "sidebar": 0.88,
        "sidebar_alt": 0.80,
        "header": 0.86,
        "overlay": 0.35,
        "input": 0.45,
        "startup": 0.90,
    },

    "2": {
        "name": "普通图片",
        "description": "推荐默认配置，透明度与可读性比较平衡",
        "workspace": 0.82,
        "modal": 0.74,
        "modal_alt": 0.68,
        "sidebar": 0.80,
        "sidebar_alt": 0.72,
        "header": 0.76,
        "overlay": 0.22,
        "input": 0.38,
        "startup": 0.82,
    },

    "3": {
        "name": "较暗图片",
        "description": "图片较暗，可以让工作区和窗口更透明",
        "workspace": 0.72,
        "modal": 0.64,
        "modal_alt": 0.58,
        "sidebar": 0.70,
        "sidebar_alt": 0.62,
        "header": 0.66,
        "overlay": 0.12,
        "input": 0.30,
        "startup": 0.72,
    },

    "4": {
        "name": "高透明",
        "description": "明显展示背景图片，适合很暗或很干净的背景",
        "workspace": 0.60,
        "modal": 0.52,
        "modal_alt": 0.46,
        "sidebar": 0.58,
        "sidebar_alt": 0.50,
        "header": 0.54,
        "overlay": 0.08,
        "input": 0.25,
        "startup": 0.60,
    },
}


def rgba(alpha):
    return f"rgba(0, 0, 0, {alpha:.2f})"


def replace_css_variable(
    content,
    variable_name,
    alpha,
):
    pattern = (
        rf"({re.escape(variable_name)}\s*:\s*)"
        rf"rgba\(\s*0\s*,\s*0\s*,\s*0\s*,\s*[\d.]+\s*\)"
    )

    return re.sub(
        pattern,
        rf"\g<1>{rgba(alpha)}",
        content,
    )


def replace_property_in_selector(
    content,
    selector,
    property_name,
    alpha,
    count=1,
):
    pattern = (
        rf"({re.escape(selector)}\s*\{{"
        rf"[\s\S]*?"
        rf"{re.escape(property_name)}\s*:\s*)"
        rf"rgba\(\s*0\s*,\s*0\s*,\s*0\s*,\s*[\d.]+\s*\)"
    )

    return re.sub(
        pattern,
        rf"\g<1>{rgba(alpha)}",
        content,
        count=count,
    )


def replace_variable_in_selector(
    content,
    selector,
    variable_name,
    alpha,
):
    pattern = (
        rf"({re.escape(selector)}\s*\{{"
        rf"[\s\S]*?"
        rf"{re.escape(variable_name)}\s*:\s*)"
        rf"rgba\(\s*0\s*,\s*0\s*,\s*0\s*,\s*[\d.]+\s*\)"
    )

    return re.sub(
        pattern,
        rf"\g<1>{rgba(alpha)}",
        content,
        count=1,
    )


def modify_css(content, preset):

    # 1. 公共变量
    content = replace_css_variable(
        content,
        "--translucent-bg",
        preset["workspace"],
    )

    content = replace_css_variable(
        content,
        "--settings-bg",
        preset["modal"],
    )

    content = replace_css_variable(
        content,
        "--settings-sidebar-bg",
        preset["sidebar"],
    )

    content = replace_css_variable(
        content,
        "--modal-overlay-bg",
        preset["overlay"],
    )

    # 2. Modal 遮罩
    content = replace_property_in_selector(
        content,
        ".modal-container.mod-dim",
        "background-color",
        preset["overlay"],
        count=0,
    )

    # 3. 通用 Modal
    content = replace_property_in_selector(
        content,
        ".modal",
        "background-color",
        preset["modal"],
    )

    content = replace_variable_in_selector(
        content,
        ".modal",
        "--background-primary",
        preset["modal"],
    )

    content = replace_variable_in_selector(
        content,
        ".modal",
        "--background-primary-alt",
        preset["modal_alt"],
    )

    content = replace_variable_in_selector(
        content,
        ".modal",
        "--background-secondary",
        preset["sidebar"],
    )

    content = replace_variable_in_selector(
        content,
        ".modal",
        "--background-secondary-alt",
        preset["sidebar_alt"],
    )

    # 4. Sidebar Layout Modal
    selector = ".modal.mod-sidebar-layout"

    content = replace_property_in_selector(
        content,
        selector,
        "background-color",
        preset["modal"],
    )

    content = replace_variable_in_selector(
        content,
        selector,
        "--background-primary",
        preset["modal"],
    )

    content = replace_variable_in_selector(
        content,
        selector,
        "--background-primary-alt",
        preset["modal_alt"],
    )

    content = replace_variable_in_selector(
        content,
        selector,
        "--background-secondary",
        preset["sidebar"],
    )

    content = replace_variable_in_selector(
        content,
        selector,
        "--background-secondary-alt",
        preset["sidebar_alt"],
    )

    # 5. Sidebar 左 / 右
    content = replace_property_in_selector(
        content,
        ".modal.mod-sidebar-layout .vertical-tab-header",
        "background-color",
        preset["sidebar"],
    )

    content = replace_property_in_selector(
        content,
        ".modal.mod-sidebar-layout .vertical-tab-content",
        "background-color",
        preset["modal"],
    )

    # 6. Modal Header
    content = replace_property_in_selector(
        content,
        ".modal .modal-header",
        "background-color",
        preset["header"],
    )

    # 7. Community Modal
    selector = ".modal.mod-community-modal"

    content = replace_property_in_selector(
        content,
        selector,
        "background-color",
        preset["modal"],
    )

    content = replace_variable_in_selector(
        content,
        selector,
        "--background-primary",
        preset["modal"],
    )

    content = replace_variable_in_selector(
        content,
        selector,
        "--background-primary-alt",
        preset["modal_alt"],
    )

    content = replace_variable_in_selector(
        content,
        selector,
        "--background-secondary",
        preset["sidebar"],
    )

    content = replace_property_in_selector(
        content,
        ".modal.mod-community-modal.mod-community-theme",
        "background-color",
        preset["modal"],
    )

    content = replace_property_in_selector(
        content,
        ".modal.mod-community-modal.mod-community-plugin",
        "background-color",
        preset["modal"],
    )

    content = replace_property_in_selector(
        content,
        ".modal.mod-community-modal .vertical-tab-header",
        "background-color",
        preset["sidebar"],
    )

    content = replace_property_in_selector(
        content,
        ".modal.mod-community-modal .vertical-tab-content",
        "background-color",
        preset["modal"],
    )

    # 8. Modal 输入框
    input_selector = (
        '.modal input[type="text"],\n'
        '.modal input[type="search"],\n'
        '.modal input[type="number"],\n'
        '.modal textarea,\n'
        '.modal select'
    )

    content = replace_property_in_selector(
        content,
        input_selector,
        "background-color",
        preset["input"],
    )

    # 9. Obsidian 启动阶段遮罩
    # 已验证有效：
    #
    # body.in-progress::after {
    #     background: rgba(0, 0, 0, ...);
    # }
    content = replace_property_in_selector(
        content,
        "body.in-progress::after",
        "background",
        preset["startup"],
    )

    return content


def main():
    current_dir = Path.cwd()
    css_path = current_dir / MY_CSS

    print()
    print("=" * 68)
    print(" Obsidian CSS 透明度调整工具 - my.css 专用")
    print("=" * 68)

    print("目标文件：{css_path}")

    if not css_path.exists():
        print("[错误] 当前目录没有找到 {MY_CSS}")
        return

    print()
    print("可连续修改透明度。")
    print("输入 1-4 应用预设；输入 q / quit / exit 退出。")

    # ========================================================
    # 连续交互循环
    # ========================================================

    while True:
        print()
        print("-" * 68)
        print("请选择透明度预设：")
        print()

        for key, preset in PRESETS.items():
            print(
                f"  [{key}] {preset['name']:<8} "
                f"- {preset['description']}"
            )

        print()
        choice = input(
            "请输入编号 [1-4]，或 q 退出："
        ).strip().lower()

        # ----------------------------------------------------
        # 退出
        # ----------------------------------------------------

        if choice in ("q", "quit", "exit"):
            print()
            print("已退出。")
            break

        # ----------------------------------------------------
        # 非法输入
        # ----------------------------------------------------

        if choice not in PRESETS:
            print()
            print("[提示] 请输入 1、2、3、4，或 q 退出。")
            continue

        preset = PRESETS[choice]

        # ----------------------------------------------------
        # 显示本次参数
        # ----------------------------------------------------

        print()
        print(f"正在应用：{preset['name']}")
        print(f"  工作区背景       : {preset['workspace']:.2f}")
        print(f"  Modal 主区域     : {preset['modal']:.2f}")
        print(f"  Modal 左侧栏     : {preset['sidebar']:.2f}")
        print(f"  Modal Header     : {preset['header']:.2f}")
        print(f"  Modal 外部遮罩   : {preset['overlay']:.2f}")
        print(f"  Modal 输入框     : {preset['input']:.2f}")
        print(f"  启动阶段遮罩     : {preset['startup']:.2f}")

        # ----------------------------------------------------
        # 每次都重新读取当前 my.css
        #
        # 这样连续修改时，第二次会基于第一次修改后的结果继续替换，
        # 不会使用脚本启动时的旧内容。
        # ----------------------------------------------------

        try:
            content = css_path.read_text(
                encoding="utf-8",
            )

            new_content = modify_css(
                content,
                preset,
            )

            if new_content == content:
                print()
                print(
                    "[提示] 本次没有产生变化。"
                    "可能当前已经是这个预设，"
                    "或者 my.css 中没有对应规则。"
                )
                continue

            css_path.write_text(
                new_content,
                encoding="utf-8",
            )

        except Exception as e:
            print()
            print(f"[失败] {e}")
            continue

        print()
        print(
            f"[完成] 已应用「{preset['name']}」到 {MY_CSS}"
        )
        print("可以继续输入其他预设进行调整。")
if __name__ == "__main__":
    main()
