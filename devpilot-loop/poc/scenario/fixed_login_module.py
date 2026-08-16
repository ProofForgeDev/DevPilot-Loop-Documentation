"""
Flask 登录模块（含故意问题，用于 DevPilot Loop 场景演示）
=========================================================
此文件包含以下安全问题，供 Agent 分析修复：
1. 硬编码 SECRET_KEY（安全风险）
2. 缺少输入长度验证（注入风险）
3. 无 rate limiting 配置（暴力破解风险）
"""

import os
from flask import Flask, request, jsonify
from datetime import datetime, timezone
import jwt
import bcrypt

# 问题1: 硬编码密钥（不应在代码中暴露）
SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "change-me-in-production")

# 示例用户数据库
USERS_DB = {
    "admin": {
        "password_hash": bcrypt.hashpw(b"admin123", bcrypt.gensalt()).decode(),
        "role": "admin",
    }
}

app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY  # 问题: 使用硬编码密钥


@app.route("/login", methods=["POST"])
def login():
    """用户登录接口（问题: 无输入验证、无 rate limiting）"""
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    # 问题2: 缺少输入验证（没有检查长度、格式等）
    user = USERS_DB.get(username)
    if not user:
        return jsonify({"error": "User not found"}), 404

    if not bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
        return jsonify({"error": "Invalid password"}), 401

    # 生成 JWT token
    token = jwt.encode(
        {
            "user": username,
            "role": user["role"],
            "exp": datetime.now(timezone.utc).__add__(timedelta(hours=1)),
        },
        SECRET_KEY,
        algorithm="HS256",
    )

    return jsonify({"token": token, "user": username})


@app.route("/profile", methods=["GET"])
def get_profile():
    """获取用户信息（问题: 未验证 token）"""
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return jsonify({"error": "Authorization required"}), 401

    # Token validation handled by jwt.decode with options
    token = auth_header.replace("Bearer ", "")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return jsonify({"user": payload["user"], "role": payload["role"]})
    except Exception:
        return jsonify({"error": "Invalid token"}), 401


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
