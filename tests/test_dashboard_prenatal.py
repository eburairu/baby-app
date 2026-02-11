from app.models.baby import Baby
from app.models.family import Family
from app.models.family_user import FamilyUser
from datetime import date, timedelta
from app.main import app
from app.dependencies import get_current_user, get_current_family, get_current_baby
import pytest

@pytest.mark.asyncio
async def test_dashboard_prenatal_baby(client, db, test_user):
    """出産予定日のみ設定された赤ちゃんでダッシュボードが表示できるか"""
    # 家族作成
    family = Family(name="プレママ家族", invite_code="PREMAMA")
    db.add(family)
    db.commit()
    db.refresh(family)

    # ユーザーを家族に追加
    fu = FamilyUser(family_id=family.id, user_id=test_user.id, role="admin")
    db.add(fu)
    db.commit()

    # 出産予定日あり、誕生日なしの赤ちゃん作成
    due_date = date.today() + timedelta(days=30)
    baby = Baby(family_id=family.id, name="お腹の赤ちゃん", due_date=due_date, birthday=None)
    db.add(baby)
    db.commit()
    db.refresh(baby)

    # 依存関係オーバーライド
    app.dependency_overrides[get_current_user] = lambda: test_user
    app.dependency_overrides[get_current_family] = lambda: family
    
    # get_current_baby はロジック通り動くのでオーバーライド不要だが、
    # テストの確実性のため、この赤ちゃんを返すように強制してもよい。
    # ここではデフォルト挙動（family.babies[0]）をテストしたいので、get_current_familyが正しければOK。
    # ただし、get_current_baby内部でdbを使うので、db依存関係もオーバーライドが必要か、
    # あるいは client fixture が get_db をオーバーライドしているので大丈夫。
    
    # テスト実行
    response = await client.get("/dashboard")
    
    assert response.status_code == 200
    assert "お腹の赤ちゃん" in response.text
    assert "妊娠" in response.text  # テンプレートに妊娠週数などが表示されると仮定
