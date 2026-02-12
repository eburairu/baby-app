#!/usr/bin/env python3
"""すべてのルーターにcookie設定を追加するスクリプト"""
import re
from pathlib import Path

def add_cookie_to_router(file_path):
    """ルーターファイルにcookie設定を追加"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # 1. Responseをインポートに追加（まだない場合）
    if 'from fastapi import' in content and 'Response' not in content.split('from fastapi import')[1].split('\n')[0]:
        content = re.sub(
            r'from fastapi import ([^)]+?)(\n|$)',
            lambda m: f'from fastapi import {m.group(1).rstrip()}, Response{m.group(2)}',
            content,
            count=1
        )

    # 2. templates.TemplateResponseの直後にクッキー設定を追加
    # パターン: return templates.TemplateResponse(...) を探して置換

    def add_cookie_after_response(match):
        indent = match.group(1)
        response_code = match.group(2)

        # すでにresponse変数を使っている場合はスキップ
        if 'response = templates.TemplateResponse' in response_code:
            return match.group(0)

        # return templates.TemplateResponse(...) を response = ... に変換
        new_code = response_code.replace('return templates.TemplateResponse', 'response = templates.TemplateResponse')

        # クッキー設定とreturnを追加
        cookie_code = f"""
{indent}# 選択された赤ちゃんIDをクッキーに保存
{indent}response.set_cookie(
{indent}    key="selected_baby_id",
{indent}    value=str(baby.id),
{indent}    max_age=7 * 24 * 60 * 60,
{indent}    httponly=False,
{indent}    samesite="lax"
{indent})
{indent}return response"""

        return f"{indent}{new_code.strip()}{cookie_code}"

    # 関数内で baby が使用されている templates.TemplateResponse のみを対象
    pattern = r'(\s+)return templates\.TemplateResponse\(((?:[^()]+|\([^()]*\))*)\)'

    # 各関数を個別に処理
    def process_function(func_match):
        func_code = func_match.group(0)

        # この関数内に baby が存在するか確認
        if 'baby: Baby' in func_code or 'baby =' in func_code:
            # templates.TemplateResponse を置換
            func_code = re.sub(pattern, add_cookie_after_response, func_code)

        return func_code

    # 各関数を処理
    content = re.sub(
        r'(@router\.(get|post|put|delete).*?\n(?:async )?def .*?(?=\n@router\.|$))',
        process_function,
        content,
        flags=re.DOTALL
    )

    # 変更があった場合のみ書き込み
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Updated: {file_path}")
        return True
    else:
        print(f"⏭️  Skipped: {file_path} (no changes needed)")
        return False

def main():
    """メイン処理"""
    router_dir = Path('app/routers')
    router_files = list(router_dir.glob('*.py'))

    print(f"Found {len(router_files)} router files\n")

    updated_count = 0
    for router_file in router_files:
        if add_cookie_to_router(router_file):
            updated_count += 1

    print(f"\n✨ Updated {updated_count} files")

if __name__ == '__main__':
    main()
