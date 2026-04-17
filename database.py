def unsubscribe(user_id, target):
    """
    從 user 的訂閱中移除 target
    """

    # 假設你用 dict 或 sqlite
    # 這裡給通用寫法（你可依你原本改）

    user_targets = get_user_targets(user_id)

    if target in user_targets:
        user_targets.remove(target)

    # 寫回資料庫（依你原本實作）
    save_user_targets(user_id, user_targets)
